import os
import urllib.parse
from functools import wraps
from flask import Flask, redirect, request, session, url_for, render_template
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


class TeslaAPIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def api_get(path):
    resp = requests.get(
        f"{TESLA_AUDIENCE}{path}",
        headers={"Authorization": f"Bearer {session['access_token']}"},
    )
    try:
        data = resp.json()
    except ValueError:
        raise TeslaAPIError(
            f"Invalid response from Tesla (HTTP {resp.status_code})", resp.status_code
        )
    if resp.status_code != 200 or (isinstance(data, dict) and data.get("error")):
        msg = (
            data.get("error_description")
            or data.get("message")
            or data.get("error")
            or f"HTTP {resp.status_code}"
        )
        raise TeslaAPIError(msg, resp.status_code)
    return data


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("access_token"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.errorhandler(TeslaAPIError)
def handle_tesla_api_error(err):
    return render_template("data.html", data=err.message, page="error"), err.status_code


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
@login_required
def me():
    return render_template("data.html", data=api_get("/api/1/users/me"), page="me")


@app.route("/charging")
@login_required
def charging():
    return render_template(
        "data.html", data=api_get("/api/1/dx/charging/history")["data"], page="charging"
    )


@app.route("/my_vehicles")
@login_required
def get_my_vehicles():
    resp = api_get("/api/1/vehicles")["response"]
    vehicle_data = []

    for i in range(len(resp)):
        new_data = {
            "display_name": resp[i]["display_name"],
            "vehicle_id": resp[i]["vehicle_id"],
            "vin": resp[i]["vin"],
        }
        vehicle_data.append(new_data)

    return render_template("data.html", data=vehicle_data, page="my_vehicles")


@app.route("/vin")
@login_required
def get_vin():
    resp = api_get("/api/1/vehicles")

    try:
        vin = resp["response"][0]["vin"]
        return vin
    except KeyError:
        return resp


@app.route("/vehicle_data")
@login_required
def vehicle_data():
    return api_get(f"/api/1/vehicles/{get_vin()}/vehicle_data")


@app.route("/monitor_charging")
@login_required
def monitor_charging():
    try:
        resp = api_get(f"/api/1/vehicles/{get_vin()}/vehicle_data")
    except TeslaAPIError as err:
        return render_template(
            "data.html", data=err.message, page="vehicle_unavailable"
        )

    amount_charged = resp["response"]["charge_state"]["charge_energy_added"]

    if resp["response"]["charge_state"]["charging_state"] == "Stopped":
        charging_message = (
            f"Charging stopped, currently added:  {amount_charged} kWh."
        )
        return render_template(
            "data.html", data=charging_message, page="monitor_charging"
        )
    elif resp["response"]["charge_state"]["charging_state"] == "Complete":
        charging_message = f"Charging finished, added:  {amount_charged} kWh."
        return render_template(
            "data.html", data=charging_message, page="monitor_charging"
        )
    elif resp["response"]["charge_state"]["charging_state"] == "Disconnected":
        charging_message = "The car is not charging."
        return render_template(
            "data.html", data=charging_message, page="monitor_charging"
        )
    else:
        charging_message = (
            f"Still charging, currently added:  {amount_charged} kWh."
        )

        return render_template(
            "data.html", data=charging_message, page="monitor_charging"
        )


@app.route("/drivers")
@login_required
def drivers():
    driver_resp = api_get(f"/api/1/vehicles/{get_vin()}/drivers")

    return render_template("data.html", data=driver_resp, page="drivers")


@app.route("/recent_alerts")
@login_required
def recent_alerts():
    return api_get(f"/api/1/vehicles/{get_vin()}/recent_alerts")
    # return render_template("data.html", data=alerts_resp, page="alerts")


@app.route("/release_notes")
@login_required
def release_notes():
    return api_get(f"/api/1/vehicles/{get_vin()}/release_notes")


@app.route("/service_data")
@login_required
def service_data():
    return api_get(f"/api/1/vehicles/{get_vin()}/service_data")


@app.route("/options")
@login_required
def options():
    options_resp = api_get(f"/api/1/dx/vehicles/options?vin={get_vin()}")

    codes = options_resp["codes"]
    options = []

    for i in range(len(codes)):
        each_option = {
            "displayName": codes[i]["displayName"],
            "isActive": codes[i]["isActive"],
        }
        options.append(each_option)

    return render_template("data.html", data=options, page="options")


@app.route("/specs")
@login_required
def specs():
    return api_get(f"/api/1/vehicles/{get_vin()}/specs")


@app.route("/warranty")
@login_required
def warranty():
    warranty_resp = api_get(f"/api/1/dx/warranty/details?vin={get_vin()}")

    active_warranty = warranty_resp["activeWarranty"]

    expired_warranty = warranty_resp["expiredWarranty"]
    upcoming_warranty = warranty_resp["upcomingWarranty"]

    warranty = []

    for i in range(len(active_warranty)):
        warranty_option = {
            "warrantyDisplayName": active_warranty[i]["warrantyDisplayName"],
            "coverageAgeInYears": active_warranty[i]["coverageAgeInYears"],
            "expirationDate": active_warranty[i]["expirationDate"],
            "expirationOdometer": active_warranty[i]["expirationOdometer"],
            "odometerUnit": active_warranty[i]["odometerUnit"],
            "warrantyExpiredOn": active_warranty[i]["warrantyExpiredOn"],
        }
        warranty.append(warranty_option)

    return render_template("data.html", data=warranty, page="warranty")


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
    app.run(host="0.0.0.0", port=5050)
