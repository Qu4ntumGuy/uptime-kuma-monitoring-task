import subprocess
 
# Open a pipe to the "ping" command
process = subprocess.Popen(["ping", "google.com"], stdout=subprocess.PIPE)
public_ip = subprocess.run(["wget -o ifonfig.me"])

from uptime_kuma_api import UptimeKumaApi,MonitorType
 
with UptimeKumaApi('http://3.145.70.251') as api:
    api.login('admin', 'root@123')
    api.add_monitor(
        type=MonitorType.HTTP,
        name="testing",
        url="https://jsmon.rashahacks.com"
        )
