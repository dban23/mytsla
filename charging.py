def charge(resp):
    while True:
        try:
            if resp["response"]["charge_state"]["charging_state"] == "Stopped":
                print("-------------------------------------------------------------")
                print("-------------------------------------------------------------")
                print(
                    "Added: ",
                    resp["response"]["charge_state"]["charge_energy_added"],
                    "kWh",
                )
                print("-------------------------------------------------------------")
                print("-------------------------------------------------------------")
            else:
                continue
        except KeyError:
            return resp
