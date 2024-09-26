import requests
import json
import urllib3
urllib3.disable_warnings()
 
url = "https://xray.cloud.getxray.app/api/v1/authenticate"

# YOU CAN GENERATE CLIENT ID AND SECRET FROM JIRA PORTAL.
# source ->
# data = {
#     "client_id": "<<SRC_CLIENT_ID>>",
#     "client_secret": "<SRC_CLIENT_SECRET>"
# }

# ========================================================================================
# destionation ->
# data = {
#     "client_id": "<DEST_CLIENT_ID>",
#     "client_secret": "<<DEST_CLIENT_SECRET>>"
# }
 
headers = {
  "Content-Type": "application/json"
}
 
response = requests.post(url, json=data, headers=headers, verify=False)
 
print("Data:")
print(response.text)
