import subprocess
from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import os

load_dotenv()

command = ['wget', '-qO-', 'https://api64.ipify.org']

try:
    result = subprocess.run(
        command, capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    print(f"Output: {e.output}")

sending_url = "http://" + result.stdout

with UptimeKumaApi(os.getenv.UPTIME_URL) as api:
    api.login(os.getenv.USER, os.getenv.PASS)
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Client-sever",
        url=sending_url,
    )
