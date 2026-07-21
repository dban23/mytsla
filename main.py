import os
import urllib.parse
import json
import requests
from dotenv import load_dotenv

load_dotenv()

DOMAIN = "mytsla.onrender.com"
TESLA_CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
TESLA_CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
TESLA_REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI")
TESLA_AUTH_URL = os.getenv("TESLA_AUTH_URL")
TESLA_TOKEN_URL = os.getenv("TESLA_TOKEN_URL")
TESLA_AUDIENCE = os.getenv("TESLA_AUDIENCE")
TESLA_SCOPES = os.getenv("TESLA_SCOPES")


def third_party_token():
    url = "https://auth.tesla.com/oauth2/v3/authorize"

    params = {
        "client_id": TESLA_CLIENT_ID,
        "redirect_uri": TESLA_REDIRECT_URI,
        "response_type": "code",
        "scope": TESLA_SCOPES,
        "state": "",
    }

    final_url = f"{url}?{urllib.parse.urlencode(params)}"

    print(final_url)
    # return redirect(final_url)


def partner_auth_token():
    url = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": TESLA_CLIENT_ID,
        "client_secret": TESLA_CLIENT_SECRET,
        "scope": "openid user_data vehicle_device_data vehicle_cmds vehicle_charging_cmds",
        "audience": TESLA_AUDIENCE,
    }

    auth_header = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, headers=auth_header, params=payload).json()
    access_token = response["access_token"]

    return access_token


def register_acc():
    access_token = partner_auth_token()
    url = f"{TESLA_AUDIENCE}/api/1/partner_accounts"

    pl = {"domain": ""}

    auth_header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, params=pl, headers=auth_header).json()

    beaut_res = json.dumps(response, indent=4, ensure_ascii=False)
    print(beaut_res)


def check_pk():
    access_token = partner_auth_token()
    url = f"{TESLA_AUDIENCE}/api/1/partner_accounts/public_key?domain={DOMAIN}"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()

    print(response)


def get_me():
    access_token = partner_auth_token()
    url = f"{TESLA_AUDIENCE}/api/1/users/me"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()
    beaut_resp = json.dumps(response, indent=4, ensure_ascii=False)

    print(beaut_resp)


get_me()


def get_charging():
    access_token = partner_auth_token()
    url = f"{TESLA_AUDIENCE}/api/1/dx/charging/history"

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
    url = f"{TESLA_AUDIENCE}/api/1/vehicles"
    # url = f"{TESLA_AUDIENCE}/api/1/users/region"

    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=auth_header).json()
    beaut_resp = json.dumps(response, indent=4, ensure_ascii=False)

    print(beaut_resp)


get_vehicle()

# get_me()
# get_vehicle()
# get_charging()
# check_pk()
# register_acc()
