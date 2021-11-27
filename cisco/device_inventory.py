import requests
import csv
import warnings
from requests.auth import HTTPBasicAuth
from getpass import getpass


warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Retrieve authtoken, refreshtoken and domain uuid
'''
address = input("Enter IP Address of the FMC: ")
username = input("Enter Username: ")
password = getpass("Enter Password: ")
'''

address = '10.106.49.51'
username = 'admin1'
password = 'cisco'


api_uri = "/api/fmc_platform/v1/auth/generatetoken"
url = "https://" + address + api_uri

response = requests.request("POST", url, verify=False, auth=HTTPBasicAuth(username, password))

accesstoken = response.headers["X-auth-access-token"]
refreshtoken = response.headers["X-auth-refresh-token"]
DOMAIN_UUID = response.headers["DOMAIN_UUID"]


# Retrieve device list

host_api_uri = "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/devices/devicerecords?expanded=true"
host_url = "https://" + address + host_api_uri
headers = { 'Content-Type': 'application/json', 'x-auth-access-token': accesstoken }

response = requests.get(host_url, headers=headers, verify = False)
r = response.json()

if response.status_code == 200:
    print("Success")
else:
    print("Failed with fetch device inventory")




# # Initialization
#
# device_dict = {'uuid': '', 'name': '', 'description': '', 'model': '',
#                'healthStatus': '', 'sw_version': '', 'healthPolicy': '',
#                'accessPolicy': '', 'hostName': '', 'license_caps': '',
#                'ftdMode': '', 'domain': ''
#                }

# Write to .csv

with open("Device Inventory.csv", "w") as f:
    w = csv.writer(f)
    my_list = r.get('items')

    for x in my_list:
        for key in {'type','links','modelId','modelNumber','advanced','keepLocalEvents','prohibitPacketTransfer'}:
            x.pop(key)
            print(my_list)
    w.writerow(my_list[0].keys())
    for x in my_list:
        w.writerow(x.values())
f.close()

# Write to .csv

#
# with open("Device Inventory.csv", "w") as f:
#     w = csv.writer(f)
#     w.writerow(device_dict.keys())
#     for x in range(num_devices):
#         uuid = r.get('items')[x].get('id')
#         name = r.get('items')[x].get('name')
#         description = r.get('items')[x].get('description')
#         model = r.get('items')[x].get('model')
#         healthStatus = r.get('items')[x].get('healthStatus')
#         sw_version = r.get('items')[x].get('sw_version')
#         healthPolicy = r.get('items')[x].get('healthPolicy').get('name')
#         accessPolicy = r.get('items')[x].get('accessPolicy').get('name')
#         hostName = r.get('items')[x].get('hostName')
#         license_caps = ",".join(r.get('items')[x].get('license_caps'))
#         ftdMode = r.get('items')[x].get('ftdMode')
#         domain = r.get('items')[x].get('metadata').get('domain').get('name')
#         device_dict = {'uuid': uuid, 'name': name, 'description': description, 'model': model,
#                        'healthStatus': healthStatus, 'sw_version': sw_version, 'healthPolicy': healthPolicy,
#                        'accessPolicy': accessPolicy, 'hostName': hostName, 'license_caps': license_caps,
#                        'ftdMode': ftdMode, 'domain': domain}
#         w.writerow(device_dict.values())
# f.close()



