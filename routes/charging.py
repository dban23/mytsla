from flask import render_template
from tesla_client import api_get, login_required, TeslaAPIError
from routes.profile import get_vin


def register_routes(app):
    @app.route("/charging")
    @login_required
    def charging():
        return render_template(
            "data.html",
            data=api_get("/api/1/dx/charging/history")["data"],
            page="charging",
        )

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