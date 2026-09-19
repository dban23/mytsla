import urllib.parse
import secrets
import requests
from flask import redirect, request, session, url_for
import config


def register_routes(app):
    @app.route("/login")
    def login():
        state = secrets.token_urlsafe(32)
        session["oauth_state"] = state

        params = {
            "client_id": config.TESLA_CLIENT_ID,
            "redirect_uri": config.TESLA_REDIRECT_URI,
            "response_type": "code",
            "scope": config.TESLA_SCOPES,
            "state": state,
        }

        url = f"{config.TESLA_AUTH_URL}?{urllib.parse.urlencode(params)}"
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
            "client_id": config.TESLA_CLIENT_ID,
            "client_secret": config.TESLA_CLIENT_SECRET,
            "code": code,
            "redirect_uri": config.TESLA_REDIRECT_URI,
        }

        resp = requests.post(config.TESLA_TOKEN_URL, data=data)
        if resp.status_code != 200:
            return f"Token exchange failed: {resp.status_code} {resp.text}", 400

        token_data = resp.json()
        session["access_token"] = token_data.get("access_token")
        session["refresh_token"] = token_data.get("refresh_token")

        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    # @app.route("/refresh")
    # def refresh():
    #     refresh_token = session.get("refresh_token")
    #     if not refresh_token:
    #         return "No refresh token stored", 400
    #
    #     data = {
    #         "grant_type": "refresh_token",
    #         "client_id": config.TESLA_CLIENT_ID,
    #         "client_secret": config.TESLA_CLIENT_SECRET,
    #         "refresh_token": refresh_token,
    #     }
    #
    #     resp = requests.post(config.TESLA_TOKEN_URL, data=data)
    #     if resp.status_code != 200:
    #         return f"Refresh failed: {resp.status_code} {resp.text}", 400
    #
    #     token_data = resp.json()
    #     session["access_token"] = token_data.get("access_token")
    #     session["refresh_token"] = token_data.get("refresh_token", refresh_token)
    #
    #     return jsonify(token_data)