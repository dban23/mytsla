import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUDIENCE = "https://fleet-api.prd.eu.vn.cloud.tesla.com"
DOMAIN = "dban23.github.io"


def partner_auth_token():
    url = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid user_data vehicle_device_data vehicle_cmds vehicle_charging_cmds",
        "audience": AUDIENCE,
    }

    auth_header = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, headers=auth_header, params=payload).json()
    access_token = response["access_token"]

    # print(access_token)
    return access_token


def register_acc():
    access_token = partner_auth_token()
    url = f"{AUDIENCE}/api/1/partner_accounts"

    pl = {"domain": "dban23.github.io"}

    auth_header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, params=pl, headers=auth_header).json()

    beaut_res = json.dumps(response, indent=4, ensure_ascii=False)
    print(beaut_res)


def check_pk():
    access_token = partner_auth_token()
    url = f"{AUDIENCE}/api/1/partner_accounts/public_key?domain={DOMAIN}"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()

    print(response)


def get_me():
    access_token = partner_auth_token()
    url = f"{AUDIENCE}/api/1/users/me"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()
    beaut_resp = json.dumps(response, indent=4, ensure_ascii=False)

    print(beaut_resp)


get_me()


def get_charging():
    access_token = partner_auth_token()
    url = f"{AUDIENCE}/api/1/dx/charging/history"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()
    beaut_resp = json.dumps(response, indent=4, ensure_ascii=False)

    print(beaut_resp)

    vin = response["data"][0]["vin"]
    return vin
    # print(vin)


def get_vehicle():
    access_token = partner_auth_token()
    # vin = get_charging()
    url = f"{AUDIENCE}/api/1/vehicles/LRW3E7FS5RC310251/vehicle_data"
    # url = f"{AUDIENCE}/api/1/users/region"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()
    beaut_resp = json.dumps(response, indent=4, ensure_ascii=False)

    print(beaut_resp)


# get_me()
# get_vehicle()
# get_charging()
# check_pk()
# register_acc()
