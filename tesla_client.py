from functools import wraps
import requests
from flask import session, redirect, url_for
import config


class TeslaAPIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def api_get(path):
    resp = requests.get(
        f"{config.TESLA_AUDIENCE}{path}",
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