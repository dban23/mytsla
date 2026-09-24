# MyTsla

MyTsla is a Flask web application that lets you sign in with your Tesla account and view data from your own vehicle using the official Tesla Fleet API.

## Features

- **Tesla SSO login** – Sign in with your Tesla account through the official OAuth2 authorization-code flow
- **Owner info** – Account name and e-mail info
- **Vehicles** – List of vehicles with display name, vehicle ID, and VIN
- **Additional drivers** – All drivers registered to your vehicle
- **Charging** – Supercharger charging history and a live charging monitor (`Stopped`, `Complete`, `Disconnected`, or in-progress kWh)
- **Car data** – Trim/option codes and warranty details resolved by VIN
- **Service** – Service data, recent alerts, and release notes
- **Full vehicle data** – Raw vehicle data response

## How it works

1. You visit `/login` – the app builds an authorization URL (client ID, redirect URI, response type `code`, state, scopes) and redirects you to Tesla's auth server.
2. After you sign in and grant consent, Tesla redirects back to `/callback` with an authorization `code` (validated against the stored OAuth `state`).
3. The app exchanges the code for an access token at the token endpoint and stores it in the Flask session.
4. Every data route calls the Tesla Fleet API with `Authorization: Bearer <access_token>` and renders the result on a page.

## Project structure

```
├── app.py                  # Flask entry point – creates the app, wires routes, error handler
├── config.py               # Loads .env and exposes configuration constants
├── tesla_client.py         # Tesla Fleet API helpers
├── routes/
│   ├── __init__.py
│   ├── auth.py             # /login, /callback, /logout
│   ├── profile.py          # /me, /my_vehicles, /drivers, /vin
│   ├── vehicle.py          # /vehicle_data, /recent_alerts, /release_notes, /service_data, /options, /warranty
│   └── charging.py         # /charging, /monitor_charging
├── requirements.txt
├── .env
├── .well-known/
│   └── appspecific/
│       └── com.tesla.3p.public-key.pem   # Public key Tesla fetches for domain verification
├── templates/              # Jinja2 templates
└── static/
    ├── css/style.css       # Stylesheet
    └── images/mytsla.png   # Logo
```

## Prerequisites

- Python 3.x
- A Tesla Developer account (free) at [developer.tesla.com](https://developer.tesla.com)
- Your OAuth application created in the Tesla Developer Portal (see below)
- Your public key served from `.well-known/appspecific/` (see domain registration below)

## Tesla Developer Portal setup

1. Create an account and log in at [developer.tesla.com](https://developer.tesla.com) → **Console**.
2. **Create a client / OAuth app**:
   - Set app name
   - Platform: Web
   - **Origin**: for local development set the origin to the same host as the redirect URI, e.g. `http://localhost:5050`
   - **Redirect URI**: e.g. `http://localhost:5050/callback` for local development (+ a second, production URL)
3. Note your **Client ID** and **Client Secret** – these go into `.env`.
4. **Scopes**: request at minimum `openid`, `user_data`, `vehicle_device_data`, `vehicle_cmds`, `vehicle_charging_cmds` (the scope string goes into `TESLA_SCOPES`).
5. **Register your public key** so the domain is trusted:
   - Place your RSA public key at `.well-known/appspecific/com.tesla.3p.public-key.pem` in the web root of your production domain. Tesla fetches this file to verify domain ownership.
   - Register the domain/account once with Tesla's Fleet API:
     1. Get a `client_credentials` token:
        ```bash
        curl -X POST 'https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token' \
          -H 'Content-Type: application/x-www-form-urlencoded' \
          -d 'grant_type=client_credentials' \
          -d 'client_id=<your_client_id>' \
          -d 'client_secret=<your_client_secret>' \
          -d 'scope=openid user_data vehicle_device_data vehicle_cmds vehicle_charging_cmds' \
          -d 'audience=https://fleet-api.prd.vn.cloud.tesla.com'
        ```
     2. Register your domain with that token:
        ```bash
        curl -X POST 'https://fleet-api.prd.vn.cloud.tesla.com/api/1/partner_accounts?domain=<your-domain>' \
          -H 'Authorization: Bearer <access_token>'
        ```
     3. Verify Tesla can fetch your public key:
        ```bash
        curl 'https://<your-domain>/.well-known/appspecific/com.tesla.3p.public-key.pem'
        ```

## Local setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv myt
   source myt/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:

   ```env
   SECRET_KEY=<a random string used to sign Flask sessions>
   TESLA_CLIENT_ID=<your client id from the Developer Portal>
   TESLA_CLIENT_SECRET=<your client secret from the Developer Portal>
   TESLA_REDIRECT_URI=http://localhost:5050/callback
   TESLA_AUTH_URL=https://auth.tesla.com/oauth2/v3/authorize
   # Official docs now point to fleet-auth.prd.vn.cloud.tesla.com, but auth.tesla.com works for most apps
   TESLA_TOKEN_URL=https://auth.tesla.com/oauth2/v3/token
   TESLA_AUDIENCE=https://fleet-api.prd.vn.cloud.tesla.com
   TESLA_SCOPES=openid user_data vehicle_device_data vehicle_cmds vehicle_charging_cmds
   ```

   > `TESLA_AUDIENCE` must match the audience you selected when creating the client in the Developer Portal (typically the production `fleet-api.prd.vn.cloud.tesla.com`).
   >
   > For production, swap `TESLA_REDIRECT_URI` to `https://<your-domain>/callback`.

4. Run the app:

   ```bash
   python3 app.py
   ```

   It serves on `http://0.0.0.0:5050`. Open `http://localhost:5050`, click **Login**, and authorize with your Tesla account.

   > **Use the literal `localhost` host.** Open the app at `http://localhost:5050` for testing. The Flask session cookie is host-scoped, so the host you open must match `TESLA_REDIRECT_URI` exactly - otherwise the callback arrives without the session cookie and you get **"Invalid state"** at `/callback`.


## Deployment (Render)

This project is configured to run on Render with gunicorn:

1. Push the repo to GitHub.
2. Create a new **Web Service** on Render connected to the repo.
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `gunicorn app:app`
5. Add the same environment variables from `.env` in the Render dashboard, but change `TESLA_REDIRECT_URI` to `https://<your-render-domain>/callback`.
6. After the first deploy, ensure the public key file is reachable at `https://<your-render-domain>/.well-known/appspecific/com.tesla.3p.public-key.pem`, then register the production domain once with Tesla (see the curl steps in *Tesla Developer Portal setup* → step 5).

## Endpoint reference

| Route                | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| `/`                  | Homepage – shows the feature dashboard when logged in, otherwise the login screen |
| `/login`             | Builds the Tesla authorization URL and redirects to Tesla SSO      |
| `/callback`          | OAuth callback – exchanges the code for tokens, validates `state`  |
| `/me`                | Owner info (full name, e-mail)              |
| `/my_vehicles`       | Your vehicles (display name, vehicle ID, VIN)                      |
| `/charging`          | Supercharger charging history                                      |
| `/monitor_charging`  | Live charging state (stopped / complete / disconnected / charging) |
| `/vehicle_data`      | Raw full vehicle data                       |
| `/vin`               | VIN of the first vehicle                                          |
| `/drivers`           | Additional drivers on your vehicle                                 |
| `/recent_alerts`     | Recent vehicle alerts                                              |
| `/release_notes`     | Recent software release notes                                      |
| `/service_data`      | Vehicle service data                                               |
| `/options`           | Option/trim codes for your VIN                                     |
| `/warranty`          | Warranty details for your VIN                                      |
| `/logout`            | Clears the session and returns to the homepage                     |

## Security notes

- Access tokens are stored **in the Flask session** (signed with `SECRET_KEY`). Use a strong, random value and rotate it in production.
- Token refresh is currently **disabled** (see the commented-out `/refresh` route in `routes/auth.py`). When a session's access token expires, log in again.
- The app calls the Fleet API directly with the user's token so no user data is stored on disk long-term.

## License

Unofficial. Not affiliated with, endorsed by, or sponsored by Tesla, Inc. "Tesla" and its marks belong to Tesla, Inc.
