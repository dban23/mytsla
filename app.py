import os
import urllib.parse
from flask import Flask, redirect, request, session, url_for, jsonify
import requests
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


# ---------- 1. Home ----------
@app.route("/")
def index():
    access_token = session.get("access_token")
    if not access_token:
        return """
        <h1>Tesla OAuth Demo</h1>
        <p>You are not logged in.</p>
        <a href="/login">Login with Tesla</a>
        """
    return """
    <h1>Tesla OAuth Demo</h1>
    <p>You are logged in.</p>
    <a href="/me">Call /users/me</a><br>
    <a href="/logout">Logout</a>
    """


# ---------- 2. Redirect user to Tesla login ----------
@app.route("/login")
def login():
    state = "random_state_value"
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


# ---------- 3. Handle callback & exchange code for tokens ----------
@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"Error from Tesla: {error}", 400

    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return "Missing code", 400

    # Optional: verify state matches session["oauth_state"]
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
    # token_data typically contains: access_token, refresh_token, id_token, expires_in, token_type
    session["access_token"] = token_data.get("access_token")
    session["refresh_token"] = token_data.get("refresh_token")

    return redirect(url_for("index"))


# ---------- 4. Call /api/1/users/me with user-context token ----------
@app.route("/me")
def me():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    url = f"{TESLA_AUDIENCE}/api/1/users/me"
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


# # ---------- 5. Refresh token endpoint (optional) ----------
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


# ---------- 6. Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
