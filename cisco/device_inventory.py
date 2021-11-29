import requests
import csv
import fpdf
import warnings

from fpdf import FPDF
from requests.auth import HTTPBasicAuth
from getpass import getpass

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Retrieve authtoken, refreshtoken and domain uuid

# address = input("Enter IP Address of the FMC: ")
# username = input("Enter Username: ")
# password = getpass("Enter Password: ")

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
print("Fetching device details ...")

if response.status_code == 200:
    print("Success")
else:
    print("Failed to fetch device inventory")


def format_fields(pass_list):
    fields = {'id','name','description','model','healthStatus','sw_version','healthPolicy',
              'accessPolicy','hostName','license_caps','ftdMode','metadata'}
    for x in pass_list:
        [x.pop(key) for key in list(x.keys()) if key not in fields]
        x['healthPolicy'] = x['healthPolicy']['name']
        x['accessPolicy'] = x['accessPolicy']['name']
        x['license_caps'] = ', '.join(x['license_caps'])
        x['metadata'] = x['metadata']['domain']['name']
        x['domain'] = x.pop('metadata')
    return pass_list


# Write to csv
def convert_to_csv(r):
    with open("Device Inventory.csv", "w") as f:
        w = csv.writer(f)
        my_list = r.get('items')
        my_list = format_fields(my_list)
        w.writerow(my_list[0].keys())
        # Write values
        for x in my_list:
            w.writerow(x.values())
    f.close()


# # Write to pdf
# def convert_to_pdf(r):
#     convert_to_csv(r)
#     with open('Device Inventory.csv', newline='') as f:
#         reader = csv.reader(f)
#         pdf = FPDF()
#         pdf.add_page()
#         page_width = pdf.w - 2 * pdf.l_margin
#         # pdf.set_font('Times', 'B', 14.0)
#         # pdf.cell(page_width, 0.0, 'Device Inventory', align='C')
#         # pdf.ln(10)
#         pdf.set_font('Courier', '', 6)
#         col_width = page_width / 4
#         pdf.ln(1)
#         th = pdf.font_size
#         for row in reader:
#             for cell in range(len(row)):
#                 pdf.cell(col_width, th, row[cell], border=1)
#             pdf.ln(th)
#         # pdf.ln(10)
#         # pdf.set_font('Times', '', 10.0)
#         # pdf.cell(page_width, 0.0, '- end of report -', align='C')
#         pdf.output('Device Inventory.pdf', 'F')
#     f.close()


output_format = ''
while output_format != 'csv':
    output_format = input("Choose output format csv or pdf: ")
    if output_format != 'csv':
        print("Output format '" + output_format + "' is not supported")
if output_format == 'csv':
    convert_to_csv(r)
    print("Done")
# elif output_format == 'pdf':
#     convert_to_pdf(r)
#     print("Done")












