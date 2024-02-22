import subprocess
from uptime_kuma_api import UptimeKumaApi,MonitorType
# Replace ['your', 'command', 'here'] with the actual command and its arguments

command = ['wget', '-qO-', 'https://api64.ipify.org']

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    print(f"Output: {e.output}")

sending_url = "http://" + result.stdout
 
with UptimeKumaApi('http://3.145.70.251') as api:
    api.login('admin', 'root@123')
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Client-sever",
        url=sending_url,
        )
