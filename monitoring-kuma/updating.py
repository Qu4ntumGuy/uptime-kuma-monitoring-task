import subprocess
import os
import re
from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import datetime

load_dotenv()

url = os.getenv("UPTIME_URL")
user_name = os.getenv("USER_NAME")
user_pass = os.getenv("USER_PASS")
monitor = os.getenv("MONITOR_NAME")


def extract_domain_name_apache(config_content):
    lines = config_content.split('\n')
    for i, line in enumerate(lines):
        if '#' in line:
            # Check the next line for ServerName
            next_line = lines[i + 1].strip()
            server_name_match = re.match(r'\bServerName\s+([^\s]+)', next_line)
            if server_name_match:
                return server_name_match.group(1)
    return None


# def extract_domain_name_nginx(config_content):
#     for line in config_content.split('\n'):
#         # Use a regular expression to match anything after "listen 80"
#         match = re.search(r'\blisten\s+80\s+([^;]+)\s*;', line)
#         if match:
#             extracted_content = match.group(1)
#             return extracted_content
#     return None


def extract_domain_name_nginx(config_content):
    for line in config_content.split('\n'):
        match = re.search(r'\bserver_name\s+([^;]+)\s*;', line)
        if match:
            extracted_content = match.group(1)
            return extracted_content
    return None


def log_error(message):
    # Log errors to a file with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - {message}\n")


def get_enabled_sites(directory):
    return os.listdir(directory)


def get_public_ip():
    try:
        # Use curl to fetch public IP from an external service
        result = subprocess.run(['curl', 'ifconfig.me'],
                                capture_output=True, text=True, check=True)
        public_ip = result.stdout.strip()
        return public_ip
    except subprocess.CalledProcessError as e:
        print(f"Error fetching public IP: {e}")
        return None


def check_process_at_port(port):
    try:
        process = subprocess.run(
            ["sudo", "lsof", "-i", f":{port}"], capture_output=True, text=True, check=True)
        return process.stdout

    except subprocess.CalledProcessError as e:
        log_error(f"Error running command: {e}")
        return ""


def check_web_servers(port, protocol):
    url = None
    process_output = check_process_at_port(port)

    if "nginx" in process_output:
        print(f"Nginx process found at port {port}")
        enabled_sites = get_enabled_sites(f'/etc/nginx/sites-enabled/')

        if not enabled_sites:
            print("No sites are enabled.")
        else:
            print("Active sites:")
            for site_config in enabled_sites:
                config_path = f'/etc/nginx/sites-available/{site_config}'
                with open(config_path, 'r') as config_file:
                    config_content = config_file.read()
                    domain_name = extract_domain_name_nginx(config_content)
                    if domain_name:
                        print(f"{domain_name}")
                        url = f"{protocol}://" + domain_name

    elif "apache2" in process_output:
        print(f"Apache2 process found at port {port}")
        enabled_sites = get_enabled_sites(f'/etc/apache2/sites-enabled/')

        if not enabled_sites:
            print("No sites are enabled.")
        else:
            print("Active sites:")
            for site_config in enabled_sites:
                config_path = f'/etc/apache2/sites-available/{site_config}'
                with open(config_path, 'r') as config_file:
                    config_content = config_file.read()
                    domain_name = extract_domain_name_apache(config_content)
                    if domain_name:
                        print(f"{domain_name}")
                        url = f"{protocol}://" + domain_name

    else:
        print(f"No Nginx or Apache2 process found at port {port}")

    return url


def main():
    sending_url = check_web_servers(80, 'http')
    print(sending_url)
    if sending_url is None:
        sending_url = check_web_servers(443, 'https')

    with UptimeKumaApi(url) as api:
        api.login(user_name, user_pass)
        data_response = api.get_monitors()

    names_array = [item['name'] for item in data_response]

    contains_client = any(monitor in name.lower() for name in names_array)

    # Find id for the given name
    client_id = None

    for item in data_response:
        if item['name'] == monitor:
            client_id = item['id']
            break

    if contains_client:
        with UptimeKumaApi(url) as api:
            api.login(user_name, user_pass)
            api.edit_monitor(client_id,
                             url=sending_url,
                             )
    else:
        with UptimeKumaApi(url) as api:
            api.login(user_name, user_pass)
            api.add_monitor(
                type=MonitorType.HTTP,
                name=monitor,
                url=sending_url,
            )


if __name__ == "__main__":
    main()
