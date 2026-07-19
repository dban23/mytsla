import os
import urllib.parse
from flask import Flask, redirect, request, session, url_for, jsonify, render_template
import requests
import secrets
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

TESLA_CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
TESLA_CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
TESLA_REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI")
TESLA_AUTH_URL = os.getenv("TESLA_AUTH_URL")
TESLA_TOKEN_URL = os.getenv("TESLA_TOKEN_URL")
TESLA_AUDIENCE = os.getenv("TESLA_AUDIENCE")
TESLA_SCOPES = os.getenv("TESLA_SCOPES")


@app.route("/")
def index():
    access_token = session.get("access_token")
    if not access_token:
        return render_template("not_logged.html")
    return render_template("index.html")


@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    params = {
        "client_id": TESLA_CLIENT_ID,
        "redirect_uri": TESLA_REDIRECT_URI,
        "response_type": "code",
        "scope": TESLA_SCOPES,
        "state": state,
    }

    url = f"{TESLA_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(url)


@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"Error from Tesla: {error}", 400

    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return "Missing code", 400

    if state != session.get("oauth_state"):
        return "Invalid state", 400

    data = {
        "grant_type": "authorization_code",
        "client_id": TESLA_CLIENT_ID,
        "client_secret": TESLA_CLIENT_SECRET,
        "code": code,
        "redirect_uri": TESLA_REDIRECT_URI,
    }

    resp = requests.post(TESLA_TOKEN_URL, data=data)
    if resp.status_code != 200:
        return f"Token exchange failed: {resp.status_code} {resp.text}", 400

    token_data = resp.json()
    session["access_token"] = token_data.get("access_token")
    session["refresh_token"] = token_data.get("refresh_token")

    return redirect(url_for("index"))


@app.route("/me")
def me():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    url = f"{TESLA_AUDIENCE}/api/1/users/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    me_resp = requests.get(url, headers=headers).json()
    # return jsonify(
    #     {
    #         "status_code": resp.status_code,
    #         "body": resp.json() if resp.text else None,
    #     }
    # )
    return render_template("data.html", data=me_resp, page="me")


@app.route("/charging")
def charging():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    url = f"{TESLA_AUDIENCE}/api/1/dx/charging/history"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers)
    return jsonify(
        {
            "status_code": resp.status_code,
            "body": resp.json() if resp.text else None,
        }
    )


@app.route("/vin")
def get_vin():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    url = f"{TESLA_AUDIENCE}/api/1/vehicles"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers).json()

    try:
        vin = resp["response"][0]["vin"]
        return vin
    except KeyError:
        return resp


@app.route("/vehicle")
def vehicle():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    vin = get_vin()

    url = f"{TESLA_AUDIENCE}/api/1/vehicles/{vin}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers)
    return jsonify(
        {
            "status_code": resp.status_code,
            "body": resp.json() if resp.text else None,
        }
    )


@app.route("/vehicle_data")
def vehicle_data():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    vin = get_vin()

    url = f"{TESLA_AUDIENCE}/api/1/vehicles/{vin}/vehicle_data"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers).json()

    return resp


@app.route("/monitor_charging")
def monitor_charging():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    vin = get_vin()

    url = f"{TESLA_AUDIENCE}/api/1/vehicles/{vin}/vehicle_data"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers).json()

    try:
        amount_charged = resp["response"]["charge_state"]["charge_energy_added"]
        if resp["response"]["charge_state"]["charging_state"] == "Stopped":
            charging_message = (
                f"Charging stopped, currently added:  {amount_charged} kWh"
            )
            return render_template(
                "data.html", data=charging_message, page="monitor_charging"
            )
        else:
            charging_message = f"Still charging, currently added:  {amount_charged} kWh"
            return render_template(
                "data.html", data=charging_message, page="monitor_charging"
            )
    except KeyError:
        return resp
    except TypeError:
        return resp


@app.route("/drivers")
def drivers():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    vin = get_vin()

    url = f"{TESLA_AUDIENCE}/api/1/vehicles/{vin}/drivers"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.get(url, headers=headers)
    return jsonify(
        {
            "status_code": resp.status_code,
            "body": resp.json() if resp.text else None,
        }
    )


# @app.route("/refresh")
# def refresh():
#     refresh_token = session.get("refresh_token")
#     if not refresh_token:
#         return "No refresh token stored", 400
#
#     data = {
#         "grant_type": "refresh_token",
#         "client_id": TESLA_CLIENT_ID,
#         "client_secret": TESLA_CLIENT_SECRET,
#         "refresh_token": refresh_token,
#     }
#
#     resp = requests.post(TESLA_TOKEN_URL, data=data)
#     if resp.status_code != 200:
#         return f"Refresh failed: {resp.status_code} {resp.text}", 400
#
#     token_data = resp.json()
#     session["access_token"] = token_data.get("access_token")
#     session["refresh_token"] = token_data.get("refresh_token", refresh_token)
#
#     return jsonify(token_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
