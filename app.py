from flask import Flask, render_template, session
import config
from tesla_client import TeslaAPIError
from routes import auth, charging, profile, vehicle

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

auth.register_routes(app)
profile.register_routes(app)
vehicle.register_routes(app)
charging.register_routes(app)


@app.route("/")
def index():
    access_token = session.get("access_token")
    if not access_token:
        return render_template("not_logged.html")
    return render_template("index.html")


@app.errorhandler(TeslaAPIError)
def handle_tesla_api_error(err):
    return render_template("data.html", data=err.message, page="error"), err.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)