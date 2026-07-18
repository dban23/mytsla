def charge(resp):
    # ovo treba bit u app.py prije poziva funkcije
    # access_token = session.get("access_token")
    # if not access_token:
    #     return redirect(url_for("login"))
    #
    # vin = get_vin()

    # url = f"{TESLA_AUDIENCE}/api/1/vehicles/{vin}/vehicle_data"
    # headers = {
    #     "Authorization": f"Bearer {access_token}",
    # }
    #
    # resp = requests.get(url, headers=headers)
    # return jsonify(
    #     {
    #         "status_code": resp.status_code,
    #         "body": resp.json() if resp.text else None,
    #     }
    # )
    try:
        charging_data = resp["body"]["response"]["charge_state"]
        # charging_data = resp["body"]["response"]["charge_state"]
        return charging_data
    except KeyError:
        return resp
