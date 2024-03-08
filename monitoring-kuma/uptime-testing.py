import json
from difflib import Differ
from uptime_kuma_api import UptimeKumaApi, MonitorType
api = UptimeKumaApi('http://3.91.229.220/')
api.login('admin', 'root@123')
# api.pause_monitor(2)
# api.resume_monitor(1)

data = api.get_monitors()
# print(json.dumps(data, indent=2))
names_array = [item['name'] for item in data]
# ids_array = [item['id'] for item in data]
print(names_array)
contains_client = any("jsmon" in name.lower() for name in names_array)
# print(contains_client)
client_id = []
for item in data:
    for name in names_array:
        if item['name'] in name.lower():
            client_id.append(item['id'])
            break

print(client_id)
