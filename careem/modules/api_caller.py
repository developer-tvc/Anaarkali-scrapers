import requests
from modules.config_loader import load_config, save_config
from modules.refresh_token import refresh_access_token
from modules.database_handler import get_completed_cancelled_orders, insert_order_to_db
from modules.email_notifier import send_failure_email
from datetime import datetime

def call_first_api():
    config = load_config()
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US",
        "application": "careemfood-mobile-v1",
        "authorization": f"Bearer {config['access_token']}",
        "lat": "25.2048",
        "lng": "55.2708",
        "meta": "web;production;1.184.0;129;chrome",
        "origin": "https://app.careemnow.com",
        "priority": "u=1, i",
        "referer": "https://app.careemnow.com/",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "time-zone": "Asia/Calcutta",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "uuid": config["deviceUuid"]
    }

    url = "https://apigateway.careemdash.com/v2/admin/orders/minimal?limit=20&filter=past&sort=new&all_localizations=true"

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        refresh_access_token()
        return call_first_api()

    if response.status_code == 200:
        orders = response.json().get('orders', [])
        completed_cancelled_orders = get_completed_cancelled_orders()

        today_date = datetime.utcnow().date()

        filtered_orders = [
            order for order in orders
            if order['id'] not in completed_cancelled_orders
            and datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%S%z').date() == today_date
        ]
        #print(filtered_orders)
        #all_order_data = []
        all_al_karama_data = []
        all_ras_al_khor_data = []    
        for order in filtered_orders:
            order_data = process_second_api(order)
            if order_data:
                #print("got order data")
                oc = order_data.pop('outlet_code')
                #print(oc)
                if oc in [1032856, 1048158]:
                    all_al_karama_data.append(order_data)
                else:
                    all_ras_al_khor_data.append(order_data)

            if order['status'] in ['Delivered', 'Cancelled']:
                insert_order_to_db(order)

        if all_al_karama_data:
            send_to_external_api(all_al_karama_data, "Karama")
            #pass
        else:# all_ras_al_khor_data:
            send_to_external_api(all_ras_al_khor_data, "Non Karama")
            #pass
        

def process_second_api(order):
    order_id = order['id']
    config = load_config()
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US",
        "application": "careemfood-mobile-v1",
        "authorization": f"Bearer {config['access_token']}",
        "lat": "25.2048",
        "lng": "55.2708",
        "meta": "web;production;1.184.0;129;chrome",
        "origin": "https://app.careemnow.com",
        "priority": "u=1, i",
        "referer": "https://app.careemnow.com/",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "time-zone": "Asia/Calcutta",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "uuid": config["deviceUuid"]
    }

    url = f"https://apigateway.careemdash.com/v2/admin/orders/{order_id}?all_localizations=true"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        second_api_response = response.json()
        return process_second_api_data(second_api_response)
    else:
        print(f"Failed to retrieve details for order {order_id}. Status code: {response.status_code}")
        return None

def process_second_api_data(second_api_response):
    try:
        order_data = {
            "order_id": second_api_response.get("id", ""),
            "order_datetime": convert_date_format(second_api_response.get("created_at", "")),
            "order_outlet": second_api_response.get("merchant", {}).get("name", ""),
            "outlet_code": second_api_response.get("merchant", {}).get("id", ""),
            "customer_name": "N/A",  
            "mobile_number": "N/A",
            "delivery_address": (second_api_response.get("dropoff_address", {}).get("nickname") or "") + " " + (second_api_response.get("dropoff_address", {}).get("street") or ""),
            "items": format_items(second_api_response.get("items", [])),
            "order_total": second_api_response.get("price", {}).get("total", ""),
            "internal_commission": (20/100) * float(second_api_response.get("price", {}).get("total", "")),
            "final_earning": float(second_api_response.get("price", {}).get("total", "")) - ((20/100) * float(second_api_response.get("price", {}).get("total", ""))),
            "sub_total": second_api_response.get("price", {}).get("original", ""),
            "discount": second_api_response.get("price", {}).get("merchant_promotion_discount", ""),
            "da_name": second_api_response.get("delivery", {}).get("captain", {}).get("name", "N/A"),
            "da_mobile": second_api_response.get("delivery", {}).get("captain", {}).get("mobile", "N/A"),
            "orderStatusCode": second_api_response.get("status", ""),
            "payment_type": second_api_response.get("payment", [{}])[0].get("type", ""),
            "payment_status": second_api_response.get("payment_status", "")
        }
        return order_data
    except Exception as e:
        print(f"Error processing second API data: {e}")
        return None

def convert_date_format(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    return dt.strftime('%Y-%m-%d %H:%M')

def format_items(items_list):
    formatted_items = []
    for item in items_list:
        count = item.get('count', 0)
        name = item.get('name', '')
        formatted_item = f"{count}X {name}"
        formatted_items.append(formatted_item)
    return formatted_items

def send_to_external_api(order_data_list, location):
    config = load_config()
    karama_url = config["karama_url"]
    ras_al_khor_url = config["ras_al_khor_url"]
    headers = {
        "Content-Type": "application/json"
    }
    if order_data_list is None or len(order_data_list) == 0:
        payload = {"data": []}
    else:
        payload = {"data": order_data_list}
    
    if location  == "Karama":
        response = requests.post(karama_url, json=payload, headers=headers)    
    else:    
        response = requests.post(ras_al_khor_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Data successfully sent to external API for ", location)
    else:
        print(f"Failed to send data to external API. Status code: {response.status_code}")
