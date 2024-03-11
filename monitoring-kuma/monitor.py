import psutil
import os
import re
import mysql.connector
from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv

load_dotenv()

UPTIME_KUMA_API_URL = os.getenv("UPTIME_KUMA_API_URL")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def mysql_connection():
    return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


client = os.popen('wget -qO- ifconfig.me').read().strip()

api = UptimeKumaApi(UPTIME_KUMA_API_URL)
api.login(DB_USER, DB_PASSWORD)


def get_running_web_servers():
    return [proc.info['name'].lower() for proc in psutil.process_iter(['pid', 'name', 'cmdline'])
            if 'apache2' in proc.info['name'].lower() or 'httpd' in proc.info['name'].lower() or 'nginx' in proc.info['name'].lower()]


def extract_domain_name(config_content, pattern):
    match = re.search(pattern, config_content)
    return match.group(1) if match else None


def extract_ssl_info(config_content, pattern):
    return bool(re.search(pattern, config_content))


def site_status(site_name, sites_enabled_path):
    site_enabled_path = os.path.join(sites_enabled_path, site_name)
    return os.path.islink(site_enabled_path) and os.path.exists(site_enabled_path)


def list_avail_sites(config_directory, file_extension=None):
    return [filename for filename in os.listdir(config_directory) if filename.endswith(file_extension)] if file_extension else os.listdir(config_directory)


def fetched_names_list(cursor, client):
    del_status = "DEL"
    fetched_name = "SELECT name, id FROM websites WHERE client = %s AND status != %s"
    cursor.execute(fetched_name, (client, del_status))
    return cursor.fetchall()


def insert_into_database(cursor, client, server_type, site_name, url, status, api):
    connection = mysql_connection()
    del_status = "DEL"
    fetched_name = "SELECT name, id FROM websites WHERE client = %s AND status != %s"
    cursor.execute(fetched_name, (client, del_status))
    fetched_data = cursor.fetchall()

    if any(site_name == data[0] for data in fetched_data):
        client_id = next(
            (uid for name, uid in fetched_data if name == site_name), None)
        update_query = "UPDATE websites SET url = %s, status = %s WHERE id = %s"
        values = (url, status, client_id)
        cursor.execute(update_query, values)
        api.edit_monitor(client_id, url=url)
        api.pause_monitor(
            client_id) if status == "DOWN" else api.resume_monitor(client_id)
        print(f"Information updated in the database for {
              server_type} - {site_name}")
    else:
        insert_query = "INSERT INTO websites (name, url, client, status) VALUES (%s, %s, %s, %s)"
        values = (site_name, url, client, status)
        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Information inserted into the database for {
              server_type} - {site_name}")
        api.add_monitor(type=MonitorType.HTTP, name=site_name, url=url)


def main():
    try:
        connection = mysql_connection()
        cursor = connection.cursor()

        running_servers = get_running_web_servers()
        available_names = []

        if running_servers:
            for server_type in set(running_servers):
                site_status_func = site_status_nginx if server_type == 'nginx' else site_status_apache
                avail_sites_func = list_avail_sites_nginx if server_type == 'nginx' else list_avail_sites_apache
                extract_domain_func = extract_domain_name_nginx if server_type == 'nginx' else extract_domain_name_apache
                extract_ssl_info_func = extract_ssl_info_nginx if server_type == 'nginx' else extract_ssl_info_apache

                avail_sites = avail_sites_func()
                if avail_sites:
                    for site in avail_sites:
                        config_file = os.path.join(
                            '/etc', server_type, 'sites-available', site)
                        sites_enabled_path = f'/etc/{
                            server_type}/sites-enabled/'

                        status = "UP" if site_status_func(
                            site, sites_enabled_path) else "DOWN"

                        try:
                            with open(config_file, 'r') as f:
                                config_content = f.read()
                                domain = extract_domain_func(config_content)
                                ssl_enabled = extract_ssl_info_func(
                                    config_content)

                                protocol = 'https' if ssl_enabled else 'http'
                                url = f"{
                                    protocol}://{domain}" if domain else None
                                site_name = os.path.splitext(site)[0]

                                available_names.append(site_name)
                                insert_into_database(
                                    cursor, client, server_type, site_name, url, status, api)
                                print(
                                    f"{url} - {site_name} - {site} - {client} - {status}")

                        except FileNotFoundError:
                            pass
                else:
                    print(f"No available sites found for {
                          server_type.capitalize()}.")
        else:
            print("Neither Apache nor Nginx is running.")

        fetched_data = fetched_names_list(cursor, client)

        delete_ids = [u_id for name,
                      u_id in fetched_data if name not in available_names]

        for del_id in delete_ids:
            del_status = "DEL"
            delete_query = "UPDATE websites SET status = %s WHERE id = %s"
            values = (del_status, del_id)
            cursor.execute(delete_query, values)
            connection.commit()
            api.delete_monitor(del_id)

    except mysql.connector.Error as e:
        print(f"Error inserting into the database: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
