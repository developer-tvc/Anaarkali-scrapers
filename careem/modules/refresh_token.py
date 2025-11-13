import requests
from modules.config_loader import load_config, save_config
from modules.email_notifier import send_failure_email, send_success_email
from datetime import datetime, timedelta

def refresh_access_token():
    print("Refreshing access token...")
    
    config = load_config()
    
    url = "https://apigateway.careemdash.com/v1/admin/token/refresh"
    
    headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US",
    "application": "careemfood-mobile-v1",
    "content-type": "application/json",
    "lat": "25.2048",
    "lng": "55.2708",
    "meta": "web;production;1.184.0;129;chrome",
    "origin": "https://app.careemnow.com",
    "priority": "u=1, i",
    "referer": "https://app.careemnow.com/",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "time-zone": "Asia/Calcutta",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "uuid": config["deviceUuid"]
    }
    
    payload = {
        "refresh_token": config["refresh_token"]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        new_data = response.json()
        token_info = new_data["token"]
        config["access_token"] = token_info["access_token"]
        print('config["access_token"]', config["access_token"])
        config["refresh_token"] = token_info["refresh_token"]
        print('config["refresh_token"]', config["refresh_token"])
        config["deviceUuid"] = new_data["uuid"]
        print('config["deviceUuid"]', config["deviceUuid"])
        
        config["expire_at"] = token_info["expire_at"]
        print('onfig["expire_at"]', config["expire_at"])
        
        save_config(config)
        send_success_email("allwynvarghese1@gmail.com")
        print("Access token refreshed and saved.")
    else:
        print(f"Failed to refresh access token. Status code: {response.status_code}")
        send_failure_email(config["gmail_user"], response.status_code, '(Careem Scraper)')

from datetime import datetime, timedelta, timezone

def check_token_expiry():
    config = load_config()

    expiry_time = datetime.fromisoformat(config["expire_at"].replace("Z", "+00:00"))

    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

    time_left = expiry_time - current_time

    if time_left < timedelta(minutes=10):
        print("Token is about to expire, refreshing token.")
        refresh_access_token()        
    else:
        print("Token is still valid.")

    days, seconds = time_left.days, time_left.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    print(f"Time left until expiry: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")
