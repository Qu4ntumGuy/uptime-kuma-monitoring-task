import psutil
import os
import configparser
import re
import mysql.connector
from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import datetime

client = os.popen('wget -qO- ifconfig.me').read().strip()

api = UptimeKumaApi("http://54.80.131.203")
api.login('admin', 'root@123')


def get_running_web_servers():
    running_servers = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            process_info = proc.info
            process_name = process_info['name'].lower()

            if 'apache2' in process_name or 'httpd' in process_name:
                running_servers.append('apache2')
            elif 'nginx' in process_name:
                running_servers.append('nginx')

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return running_servers


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


def extract_domain_name_nginx(config_content):
    for line in config_content.split('\n'):
        match = re.search(r'\bserver_name\s+([^;]+)\s*;', line)
        if match:
            extracted_content = match.group(1)
            return extracted_content
    return None


def extract_ssl_info_apache(config_content):
    ssl_match = re.search(r'\bSSLEngine\s+(on|off)', config_content)
    if ssl_match and ssl_match.group(1) == 'on':
        return True
    return False


def extract_ssl_info_nginx(config_content):
    ssl_match = re.search(r'\blisten\s+443 ssl', config_content)
    if ssl_match:
        return True
    return False


def site_status_nginx(site_name):
    nginx_sites_enabled_path = '/etc/nginx/sites-enabled/'
    # Check if the specified site name is present in the sites-enabled directory
    site_enabled_path = os.path.join(nginx_sites_enabled_path, site_name)
    return os.path.islink(site_enabled_path) and os.path.exists(site_enabled_path)


def site_status_apache(site_name):
    nginx_sites_enabled_path = '/etc/apache2/sites-enabled/'
    # Check if the specified site name is present in the sites-enabled directory
    site_enabled_path = os.path.join(nginx_sites_enabled_path, site_name)
    return os.path.islink(site_enabled_path) and os.path.exists(site_enabled_path)


def list_avail_sites_nginx():
    avail_sites = []
    config_directory = '/etc/nginx/sites-available/'

    for filename in os.listdir(config_directory):
        avail_sites.append(filename)

    return avail_sites


def list_avail_sites_apache():
    avail_sites = []
    config_directory = '/etc/apache2/sites-available/'

    for filename in os.listdir(config_directory):
        if filename.endswith(".conf"):
            avail_sites.append(filename)

    return avail_sites


def fetched_names_list():
    try:
        connection = mysql.connector.connect(
            host="54.80.131.203",
            user="admin",
            password="root@123",
            database="kuma"
        )
        cursor = connection.cursor()
        fetched_name = "SELECT name, id FROM websites WHERE client = %s"
        fetching_value = client
        cursor.execute(fetched_name, (fetching_value,))
        fetched_data = cursor.fetchall()

        # fetched_data = [row[0] for row in fetched_data]
        return fetched_data

    except mysql.connector.Error as e:
        print(f"Error inserting into the database: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def insert_into_database(server_type, site_name, url, client, status):
    try:
        connection = mysql.connector.connect(
            host="54.80.131.203",
            user="admin",
            password="root@123",
            database="kuma"
        )
        cursor = connection.cursor()
        del_status = "DEL"
        fetched_name = "SELECT name, id FROM websites WHERE client = %s AND status != %s"
        fetching_value = (client, del_status)
        cursor.execute(fetched_name, fetching_value)
        fetched_data = cursor.fetchall()

        if any(site_name in data[0] for data in fetched_data):
            update_query = "UPDATE websites SET url = %s, status = %s WHERE name = %s"
            values = (url, status, site_name)
            cursor.execute(update_query, values)
            connection.commit()

            client_id = None
            for row in fetched_data:
                name = row[0]
                uid = row[1]
                if name == site_name:
                    client_id = uid
                    break

            api.edit_monitor(client_id, url=url)

            if status == "DOWN":
                api.pause_monitor(client_id)
                print(f"Monitor paused for {site_name}")
            else:
                api.resume_monitor(client_id)
                print(f"Monitor resumed for {site_name}")

            print(f"Information updated in the database for {
                  server_type} - {site_name}")

        else:
            insert_query = "INSERT INTO websites (name, url, client, status) VALUES (%s, %s, %s, %s)"
            values = (site_name, url, client, status)
            cursor.execute(insert_query, values)
            connection.commit()
            print(f"Information inserted into the database for {
                  server_type} - {site_name}")
            api.add_monitor(
                type=MonitorType.HTTP,
                name=site_name,
                url=url
            )

    except mysql.connector.Error as e:
        print(f"Error inserting into the database: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    try:
        connection = mysql.connector.connect(
            host="54.80.131.203",
            user="admin",
            password="root@123",
            database="kuma"
        )
        cursor = connection.cursor()

        running_servers = get_running_web_servers()
        fetched_data = fetched_names_list()
        available_names = []
        if running_servers:
            for server_type in set(running_servers):
                if server_type == 'nginx':
                    site_status = site_status_nginx
                    avail_sites = list_avail_sites_nginx()
                    extract_domain_func = extract_domain_name_nginx
                    extract_ssl_info_func = extract_ssl_info_nginx
                elif server_type == 'apache2':
                    site_status = site_status_apache
                    avail_sites = list_avail_sites_apache()
                    extract_domain_func = extract_domain_name_apache
                    extract_ssl_info_func = extract_ssl_info_apache
                else:
                    print(f"Unsupported server type: {server_type}")
                    continue
                if avail_sites:
                    for site in avail_sites:

                        config_file = os.path.join(
                            '/etc', server_type, 'sites-available', site)

                        status = None
                        if site_status(site):
                            status = "UP"
                        else:
                            status = "DOWN"

                        try:
                            with open(config_file, 'r') as f:
                                config_content = f.read()
                                domain = extract_domain_func(config_content)
                                ssl_enabled = extract_ssl_info_func(
                                    config_content)

                                if ssl_enabled:
                                    protocol = 'https'
                                else:
                                    protocol = 'http'

                                url = f"{protocol}://{domain}"
                                site_name = os.path.splitext(site)[0]

                                available_names.append(site_name)

                                # print(type(client))
                                # Insert into the database
                                insert_into_database(
                                    server_type, site_name, url, client, status)

                                # Print the information
                                print(
                                    f"{url} - {site_name} - {site} - {client} - {status}")

                        except FileNotFoundError:
                            pass
                else:
                    print(f"No available sites found for {
                        server_type.capitalize()}.")
        else:
            print("Neither Apache nor Nginx is running.")

        delete_ids = []
        for name, u_id in fetched_data:
            if name not in available_names:
                delete_ids.append(u_id)

        for del_id in delete_ids:
            del_status = "DEL"
            delete_query = "UPDATE websites SET status = %s WHERE id = %s"
            values = (del_status, del_id)
            cursor.execute(delete_query, values)
            connection.commit()
            api.delete_monitor(del_id)

        print(delete_ids)
        print(fetched_data)
        print(available_names)

    except mysql.connector.Error as e:
        print(f"Error inserting into the database: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
