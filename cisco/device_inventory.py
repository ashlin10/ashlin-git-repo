import requests
import csv
import warnings
import sys
import os
from requests.auth import HTTPBasicAuth
from getpass import getpass

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

print('===========================================================')
print('|                    Enter FMC details                    |')
print('===========================================================')

address = input("Enter IP Address of the FMC: ")
username = input("Enter Username: ")
password = getpass("Enter Password: ")


# Authentication

def authentication():
    try:
        api_uri = "/api/fmc_platform/v1/auth/generatetoken"
        url = "https://" + address + api_uri

        response = requests.request("POST", url, verify=False, auth=HTTPBasicAuth(username, password))
        accesstoken = response.headers["X-auth-access-token"]
        refreshtoken = response.headers["X-auth-refresh-token"]
        DOMAIN_UUID = response.headers["DOMAIN_UUID"]
    except Exception:
        print(response.json().get('error').get('messages')[0].get('description'))
        sys.exit()
    return accesstoken,refreshtoken,DOMAIN_UUID


# Retrieve device list

def fetch_device_inventory(accesstoken,refreshtoken,DOMAIN_UUID):
    try:
        host_api_uri = "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/devices/devicerecords?expanded=true"
        host_url = "https://" + address + host_api_uri
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': accesstoken}
        print("Fetching device details ...")
        response = requests.get(host_url, headers=headers, verify = False)
        if response.status_code == 200:
            print("Device inventory retrieved successfully")
        else:
            raise Exception
    except Exception:
        print("Failed to fetch device inventory: " + response.json().get('error').get('messages')[0].get('description'))
        sys.exit()
    return response.json()


# Format fields

def format_fields(pass_list):
    fields = {'id','name','model','healthStatus','sw_version','healthPolicy',
              'accessPolicy','license_caps','ftdMode','metadata'}
    for x in pass_list:
        [x.pop(key) for key in list(x.keys()) if key not in fields]
        x['healthPolicy'] = x['healthPolicy']['name']
        x['accessPolicy'] = x['accessPolicy']['name']
        x['license_caps'] = ', '.join(x['license_caps'])
        x['domain'] = x['metadata']['domain']['name']
        if float(x['sw_version'][0:3]) >= 6.7:
            x['deviceSerialNumber'] = x['metadata']['deviceSerialNumber']
            x['snortVersion'] = x['metadata']['snortVersion']
            x['sruVersion'] = x['metadata']['sruVersion']
            x['vdbVersion'] = x['metadata']['vdbVersion']
        x.pop('metadata')
    return pass_list


# Write to csv

def convert_to_csv(r):
    with open("Device Inventory.csv", "w") as f:
        w = csv.writer(f)
        my_list = r.get('items')
        my_list = format_fields(my_list)
        # Find largest element in list
        max_element = 0
        for x in range(len(my_list) - 1):
            if len(my_list[x]) > max_element:
                max_element = x
        # Print key
        w.writerow(my_list[max_element].keys())
        # Print values
        for x in my_list:
            w.writerow(x.values())
    f.close()


accesstoken,refreshtoken,DOMAIN_UUID = authentication()
r = fetch_device_inventory(accesstoken,refreshtoken,DOMAIN_UUID)
convert_to_csv(r)
print("Output is saved with file named 'Device Inventory.csv' at " + os.getcwd())












