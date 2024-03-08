import json
from difflib import Differ


def compare_json(json1, json2):
    # Convert JSON strings to Python objects
    obj1 = json.loads(json1)
    obj2 = json.loads(json2)

    # Use the Differ class to find the differences
    differ = Differ()
    diff = list(differ.compare(json.dumps(obj1, indent=2).splitlines(
        keepends=True), json.dumps(obj2, indent=2).splitlines(keepends=True)))

    return diff


response1 = '''
{
      "id": 1,
      "name": "jsmon",
      "description": null,
      "pathName": "jsmon",
      "parent": null,
      "childrenIDs": [],
      "url": "https://jsmon.rashahacks.com",
      "method": "GET",
      "hostname": null,
      "port": null,
      "maxretries": 0,
      "weight": 2000,
      "active": true,
      "forceInactive": false,
      "type": "http",
      "timeout": 48,
      "interval": 60,
      "retryInterval": 60,
      "resendInterval": 0,
      "keyword": null,
      "invertKeyword": false,
      "expiryNotification": false,
      "ignoreTls": false,
      "upsideDown": false,
      "packetSize": 56,
      "maxredirects": 10,
      "accepted_statuscodes": [
        "200-299"
      ],
      "dns_resolve_type": "A",
      "dns_resolve_server": "1.1.1.1",
      "dns_last_result": null,
      "docker_container": "",
      "docker_host": null,
      "proxyId": null,
      "notificationIDList": [],
      "tags": [],
      "maintenance": false,
      "mqttTopic": "",
      "mqttSuccessMessage": "",
      "databaseQuery": null,
      "authMethod": "",
      "grpcUrl": null,
      "grpcProtobuf": null,
      "grpcMethod": null,
      "grpcServiceName": null,
      "grpcEnableTls": false,
      "radiusCalledStationId": null,
      "radiusCallingStationId": null,
      "game": null,
      "gamedigGivenPortOnly": true,
      "httpBodyEncoding": "json",
      "jsonPath": null,
      "expectedValue": null,
      "kafkaProducerTopic": null,
      "kafkaProducerBrokers": [],
      "kafkaProducerSsl": false,
      "kafkaProducerAllowAutoTopicCreation": false,
      "kafkaProducerMessage": null,
      "screenshot": null,
      "headers": null,
      "body": null,
      "grpcBody": null,
      "grpcMetadata": null,
      "basic_auth_user": null,
      "basic_auth_pass": null,
      "oauth_client_id": null,
      "oauth_client_secret": null,
      "oauth_token_url": null,
      "oauth_scopes": null,
      "oauth_auth_method": "client_secret_basic",
      "pushToken": null,
      "databaseConnectionString": null,
      "radiusUsername": null,
      "radiusPassword": null,
      "radiusSecret": null,
      "mqttUsername": "",
      "mqttPassword": "",
      "authWorkstation": null,
      "authDomain": null,
      "tlsCa": null,
      "tlsCert": null,
      "tlsKey": null,
      "kafkaProducerSaslOptions": {
        "mechanism": "None"
      },
      "includeSensitiveData": true
    }
'''

response2 = '''
{
      "id": 5,
      "name": "jsmon",
      "description": null,
      "pathName": "jsmon",
      "parent": null,
      "childrenIDs": [],
      "url": "https://example.com",
      "method": "GET",
      "hostname": null,
      "port": null,
      "maxretries": 0,
      "weight": 2000,
      "active": true,
      "forceInactive": false,
      "type": "http",
      "timeout": 48,
      "interval": 60,
      "retryInterval": 60,
      "resendInterval": 0,
      "keyword": null,
      "invertKeyword": false,
      "expiryNotification": false,
      "ignoreTls": false,
      "upsideDown": false,
      "packetSize": 56,
      "maxredirects": 10,
      "accepted_statuscodes": [
        "200-299"
      ],
      "dns_resolve_type": "A",
      "dns_resolve_server": "1.1.1.1",
      "dns_last_result": null,
      "docker_container": "",
      "docker_host": null,
      "proxyId": null,
      "notificationIDList": [],
      "tags": [],
      "maintenance": false,
      "mqttTopic": "",
      "mqttSuccessMessage": "",
      "databaseQuery": null,
      "authMethod": "",
      "grpcUrl": null,
      "grpcProtobuf": null,
      "grpcMethod": null,
      "grpcServiceName": null,
      "grpcEnableTls": false,
      "radiusCalledStationId": null,
      "radiusCallingStationId": null,
      "game": null,
      "gamedigGivenPortOnly": true,
      "httpBodyEncoding": "json",
      "jsonPath": null,
      "expectedValue": null,
      "kafkaProducerTopic": null,
      "kafkaProducerBrokers": [],
      "kafkaProducerSsl": false,
      "kafkaProducerAllowAutoTopicCreation": false,
      "kafkaProducerMessage": null,
      "screenshot": null,
      "headers": null,
      "body": null,
      "grpcBody": null,
      "grpcMetadata": null,
      "basic_auth_user": null,
      "basic_auth_pass": null,
      "oauth_client_id": null,
      "oauth_client_secret": null,
      "oauth_token_url": null,
      "oauth_scopes": null,
      "oauth_auth_method": "client_secret_basic",
      "pushToken": null,
      "databaseConnectionString": null,
      "radiusUsername": null,
      "radiusPassword": null,
      "radiusSecret": null,
      "mqttUsername": "",
      "mqttPassword": "",
      "authWorkstation": null,
      "authDomain": null,
      "tlsCa": null,
      "tlsCert": null,
      "tlsKey": null,
      "kafkaProducerSaslOptions": {
        "mechanism": "None"
      },
      "includeSensitiveData": true
    }
'''

differences = compare_json(response1, response2)

# Display the differences in a tabular form
print("Differences between JSON responses:")
print("{:<10} {:<50} {:<50}".format(
    "Line", "JSON Response 1", "JSON Response 2"))
print("=" * 110)
for i, line in enumerate(differences, start=1):
    print("{:<10} {:<50} {:<50}".format(i, line.strip(), ''))
