import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import json
from collections import OrderedDict
from datetime import datetime


# Define the URLs
base_url = "https://manage.eateasily.com/merchant/order/rest_tab_view_details/"
source_url = "https://manage.eateasily.com/merchant/order/rest_tab_view/2/0"

# Define cookies
cookies = {
    "PHPSESSID": "1dl3vh35td25f30f0lm8iiuah5",
    "__utmc": "43743929",
    "__utmz": "43743929.1732177966.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "__zlcmid": "1OqnBaymbaUBkPR",
    "admin_manage_eateasily_2015": "Y53vZFtTpT9VEXzmUd%2BP6cr1FTrEvNJAk29iHef1lmOff33p8AGV0z5pjJGumryhpt%2BoKIEtBRM7zsZ6ostozTwSvXKPCicjKSf2lcmQbkibdO2VtBtD4mergj5IdKGB5hmKZAISz17%2BuX5AJo31RBu0LSPoXyzEGx8yZBcbf96njgc%2FzLvdH6B5bGYmxaugqn5LG%2B5YIe2mRj9Qpxwb7vTkTOOxhHuXyJNbD%2FZyc494XTQV5HJCQzi5SezfpePB33AxIbkAaUeLRhobkHwt3Ai%2FMYzCCIrybZ1hj4JgdWcPC9kTJVoqPNWvGCWdOS%2B%2BZ50cl3idJcfLh3LPJZqluDf%2FSZAuD0lAyGTEvJF47F2ge9QqZ1k1QhX9I4XZBydkqQmkItokrGAV%2FrTCPvPmPsysz1M7Db4xxtom%2F1sSHZ4GMMpc2RWuoM05Mcr6LAqJ%2F%2F7uZeVv6AoFKbYevMi1IHcvNhLs0E%2F2dWvrKtz%2F0og%2Boeqh2JwoyYdDyNRju7gnbzxQM0MnudTnhAahYkVbY01Eah4dnlOoseaiwqP%2FXHvt8QSswCfj1XdrCqMgoaQ8odUl9b6h0EkCuY61Aw2KwZEl%2BL2SBVk%2Bq6XFrbylOHqa5V0QGMWsFEZUnR0ZSB3tM7dTKouJ1Trgpv7HDvrO596%2FPghANoz%2BQRjqBlDPQVPF2wpHxtzf24h8sy24p3vSveDTKPb%2Ffo87WScIXnN8yjP7c7EaNOyZRpaswWkjDzwtY0bP%2BlGDsYR4zTEw0JQdLczTa0JABn2dibN5%2BNnqkx76cxdwIDSlMzag3TK%2BihTcl3kQZeev3eMekct5Vipx18tu8kfezgdtFcIt3R6Bun6Zza6swK3ORV87nqCVCJLBoa%2BXhiHJtzidaPNABqtA8AVPZZF2CtYnU8Gbv0pgZU2KzIZzYhp2%2BF%2B83cPuP1Zo70gxORY14w6wl%2FfbrgCNFXEB68v41IWW4F%2B0hShduqbBMrSQfY1g0AwukEhSsL8HljE0lGbMqEBvn67U2G%2Bz",
    "__utma": "43743929.1848000956.1732177966.1732189696.1732251585.3",
    "__utmt": "1",
    "__utmb": "43743929.2.10.1732251585"
}

# Define headers
headers = {
    "Referer": "https://manage.eateasily.com/merchant/order/rest_tab_view/2/0",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# SQLite database setup
DB_NAME = "orders.db"

def setup_database():
    """Create the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            order_status TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_order_to_db(order_id, order_status):
    """Save or update the order in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if the order already exists
    cursor.execute("SELECT order_status FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    
    if row:
        # Update the status if it's not 'Fulfilled' or 'Cancelled'
        if row[0] not in ["Delivered", "Cancelled"]:
            cursor.execute("UPDATE orders SET order_status = ? WHERE order_id = ?", (order_status, order_id))
    else:
        # Insert new order
        cursor.execute("INSERT INTO orders (order_id, order_status) VALUES (?, ?)", (order_id, order_status))
    
    conn.commit()
    conn.close()

# Function to extract arguments from the main page
"""def extract_arguments():
    response = requests.get(source_url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(attrs={"onclick": True})

        arguments = []
        for tag in tags:
            onclick_value = tag['onclick']
            if 'loadOpenDrawer' in onclick_value:
                match = re.search(r'loadOpenDrawer\((\d+),', onclick_value)
                if match:
                    arguments.append(match.group(1))
        return arguments
    else:
        print(f"Failed to fetch the source page. Status code: {response.status_code}")  
        return []"""

def extract_arguments():
    # Define the payload for the POST request
    payload = {
        "search_text": "",
        "search_date": datetime.today().strftime("%Y-%m-%d"),
        "order_search": "Search"
    }

    # Send the POST request with the payload
    response = requests.post(source_url, headers=headers, cookies=cookies, data=payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(attrs={"onclick": True})

        arguments = []
        for tag in tags:
            onclick_value = tag['onclick']
            if 'loadOpenDrawer' in onclick_value:
                match = re.search(r'loadOpenDrawer\((\d+),', onclick_value)
                if match:
                    arguments.append(match.group(1))
        return arguments
    else:
        print(f"Failed to fetch the source page. Status code: {response.status_code}")
        return []


# Function to extract data from the HTML of the order details page
def extract_order_details(order_id):
    """Extract order details from the HTML and return as a dictionary."""
    response = requests.get(f"{base_url}{order_id}", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract fields in the specified order
        order_details = OrderedDict()
        order_details["order_id"] = order_id
        
        # Get the last 'order-st-title' div
        order_status_tags = soup.find_all("div", class_="order-st-title")
        order_details["order_status"] = (
            order_status_tags[-1].text.strip() if order_status_tags else None
        )

        if order_details["order_status"] == 'Fulfilled':
            order_details["order_status"] = 'Delivered'
        elif order_details["order_status"] == 'Order Not Accepted':
            order_details["order_status"] = 'Cancelled'
        
        order_details["restaurant_name"] = soup.find("h1").text.strip() if soup.find("h1") else None
        order_details["customer_name"] = soup.find("div", string="Name").find_next_sibling("div").text.strip() if soup.find("div", string="Name") else None
        order_details["customer_contact"] = soup.find("div", string="Mobile").find_next_sibling("div").text.strip() if soup.find("div", string="Mobile") else None
        
        # Extract delivery agent details
        delivery_agent_block = soup.find("div", class_="od-card")
        if delivery_agent_block:
            rows = delivery_agent_block.find_all("div", class_="row")
            if len(rows) >= 2:
                delivery_agent_name_row = rows[0]
                delivery_agent_contact_row = rows[1]

                # Extract delivery agent name
                name_div = delivery_agent_name_row.find("div", class_="col-sm-9")
                order_details["delivery_agent_name"] = (
                    name_div.text.strip(": ").strip() if name_div else None
                )

                # Extract delivery agent contact
                contact_div = delivery_agent_contact_row.find("div", class_="col-sm-9")
                order_details["delivery_agent_contact"] = (
                    contact_div.text.strip(": ").strip() if contact_div else None
                )
            else:
                order_details["delivery_agent_name"] = None
                order_details["delivery_agent_contact"] = None
        else:
            order_details["delivery_agent_name"] = None
            order_details["delivery_agent_contact"] = None
        
        # Extract order items in the format "quantity X item name"
        order_items = []
        item_rows = soup.select("table.od-table tbody tr")
        for row in item_rows:
            quantity = row.find("th", class_="qty")
            item = row.find("div", class_="item-name")
            if quantity and item:
                order_items.append(f"{quantity.text.strip()} {item.text.strip()}")
        order_details["order_items"] = ", ".join(order_items)

        # Function to clean and convert price to float
        def clean_price(value, remove_minus=False):
            if value:
                cleaned_value = value.replace("AED", "").strip()
                if remove_minus:
                    cleaned_value = cleaned_value.lstrip("-")
                return float(cleaned_value)
            return 0.0

        # Extract financial details as floats
        order_details["sub_total"] = clean_price(
            soup.find("tr", class_="subtotal").find("td", class_="amount").text 
            if soup.find("tr", class_="subtotal") else "0"
        )
        coupon_row = soup.find("tr", class_="order-sponsored")
        order_details["coupon"] = clean_price(
            coupon_row.find("td", class_="amount").text if coupon_row else "0",
            remove_minus=True
        )
        order_details["delivery_charge"] = clean_price(
            soup.find("tr", string="Delivery charge").find_next_sibling("td").text 
            if soup.find("tr", string="Delivery charge") else "0"
        )
        order_details["total"] = clean_price(
            soup.find("tr", class_="order-total").find("td", class_="amount").text 
            if soup.find("tr", class_="order-total") else "0"
        )

        # Commission data
        order_details["internal_commission"] = round((34 / 100) * float(order_details["total"]), 3)
        order_details["final_earning"] = round(float(order_details["total"]) - order_details["internal_commission"], 3)

        # Extract payment status
        payment_tag = soup.find("div", class_="payment-tag")
        order_details["payment_status"] = payment_tag.text.strip() if payment_tag else None

        # Extract order date and time without AM/PM
        date_row = soup.find("div", class_="order-st-date")
        time_row = soup.find("div", class_="order-st-time")
        if date_row and time_row:
            raw_datetime = f"{date_row.text.strip()} {time_row.text.strip()}"
            parsed_datetime = datetime.strptime(raw_datetime, "%d-%b-%Y %I:%M %p")
            order_details["order_date_time"] = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            order_details["order_date_time"] = None

        return order_details  # Return a dictionary
    else:
        print(f"Failed to fetch order details for order ID: {order_id}")
        return None

# Main script
# External API endpoint
external_api_url = "https://keralaanaarkali.com/api/get-smiles-data"

# Main script
if __name__ == "__main__":
    # Step 1: Setup the database
    setup_database()

    # Step 2: Extract arguments
    order_arguments = extract_arguments()

    # Step 3: Process each order
    all_order_details = []
    for order_id in order_arguments:
        order_data = extract_order_details(order_id)
        if order_data:
            save_order_to_db(order_data["order_id"], order_data["order_status"])
            all_order_details.append(order_data)

    # Step 4: Prepare JSON payload
    api_payload = {"data": all_order_details}

    # Debugging: Print the JSON payload to verify format
    import json
    #print("JSON Payload:")
    #print(json.dumps(api_payload, indent=2))

    # Step 5: Send JSON to external API
    response = requests.post(external_api_url, json=api_payload)
    if response.status_code == 200:
        print("Successfully sent data to API")
    else:
        print(f"Failed to send data to API: {response.status_code}")


