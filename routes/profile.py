from flask import render_template
from tesla_client import api_get, login_required


@login_required
def get_vin():
    resp = api_get("/api/1/vehicles")

    try:
        vin = resp["response"][0]["vin"]
        return vin
    except KeyError:
        return resp


def register_routes(app):
    app.route("/vin")(get_vin)

    @app.route("/me")
    @login_required
    def me():
        return render_template("data.html", data=api_get("/api/1/users/me"), page="me")

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

    @app.route("/drivers")
    @login_required
    def drivers():
        driver_resp = api_get(f"/api/1/vehicles/{get_vin()}/drivers")

        return render_template("data.html", data=driver_resp, page="drivers")