import subprocess
from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import os

load_dotenv()

command = ['wget', '-qO-', 'https://api64.ipify.org']
# nginxConfigPath = "/etc/nginx/sites-enabled/default"

try:
    result = subprocess.run(
        command, capture_output=True, text=True, check=True)
    # print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    print(f"Output: {e.output}")

sending_url = "http://" + result.stdout

url = os.getenv("UPTIME_URL")
user_name = os.getenv("USER_NAME")
user_pass = os.getenv("USER_PASS")

with UptimeKumaApi(url) as api:
    api.login(user_name, user_pass)
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Client-sever",
        url=sending_url,
    )
