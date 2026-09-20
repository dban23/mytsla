from flask import render_template
from tesla_client import api_get, login_required
from routes.profile import get_vin


def register_routes(app):
    @app.route("/vehicle_data")
    @login_required
    def vehicle_data():
        return api_get(f"/api/1/vehicles/{get_vin()}/vehicle_data")

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
        options_list = []

        for i in range(len(codes)):
            each_option = {
                "displayName": codes[i]["displayName"],
                "isActive": codes[i]["isActive"],
            }
            options_list.append(each_option)

        return render_template("data.html", data=options_list, page="options")

    # this endpoint is not working as expected - opened ticket on Tesla dev portal
    # @app.route("/specs")
    # @login_required
    # def specs():
    #     return api_get(f"/api/1/vehicles/{get_vin()}/specs")

    @app.route("/warranty")
    @login_required
    def warranty():
        warranty_resp = api_get(f"/api/1/dx/warranty/details?vin={get_vin()}")

        active_warranty = warranty_resp["activeWarranty"]

        expired_warranty = warranty_resp["expiredWarranty"]
        upcoming_warranty = warranty_resp["upcomingWarranty"]

        warranty_list = []

        for i in range(len(active_warranty)):
            warranty_option = {
                "warrantyDisplayName": active_warranty[i]["warrantyDisplayName"],
                "coverageAgeInYears": active_warranty[i]["coverageAgeInYears"],
                "expirationDate": active_warranty[i]["expirationDate"],
                "expirationOdometer": active_warranty[i]["expirationOdometer"],
                "odometerUnit": active_warranty[i]["odometerUnit"],
                "warrantyExpiredOn": active_warranty[i]["warrantyExpiredOn"],
            }
            warranty_list.append(warranty_option)

        return render_template("data.html", data=warranty_list, page="warranty")
