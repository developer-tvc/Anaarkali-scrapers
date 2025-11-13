import requests
from modules.config_loader import load_config, save_config
from modules.email_notifier import send_failure_email

def refresh_access_token():
    print("Refreshing access token...")
    
    config = load_config()
    
    url = "https://bff-api.eu.prd.portal.restaurant/auth/v4/oneweb/refresh"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ml;q=0.7",
        "content-length": "820",
        "content-type": "application/json",
        "origin": "https://partner-app.talabat.com",
        "priority": "u=1, i",
        "referer": "https://partner-app.talabat.com/",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "x-app-name": "one-web",
        "x-app-version": "2.8.1",
    }
    
    payload = {
        "device_token": config["device_token"],
        "refresh_token": config["refresh_token"]
    }
    
    # Make the request to refresh the token
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        new_data = response.json()["keymaker"]
        config["access_token"] = new_data["access_token"]
        config["refresh_token"] = new_data["refresh_token"]
        config["device_token"] = new_data["device_token"]
        save_config(config)
        print("Access token refreshed and saved.run on 28nov")
    else:
        print(f"Failed to refresh access token. Status code: {response.status_code}")
        # send_failure_email(config["gmail_user"], response.status_code)
