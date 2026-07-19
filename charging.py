from flask import render_template


def charge(resp):
    try:
        amount_charged = resp["response"]["charge_state"]["charge_energy_added"]
        if resp["response"]["charge_state"]["charging_state"] == "Stopped":
            message = f"Charging stopped, currently added:  {amount_charged} kWh"
            return render_template("charging.html", message=message)
        else:
            message = f"Still charging, currently added:  {amount_charged} kWh"
            return render_template("charging.html", message=message)
    except KeyError:
        return resp
