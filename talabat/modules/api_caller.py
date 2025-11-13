import requests
from datetime import datetime
import json

from modules.config_loader import load_config
from modules.refresh_token import refresh_access_token
from modules.database import get_completed_cancelled_orders, add_order_to_db, create_table

def call_first_api():
    create_table()

    completed_cancelled_orders = get_completed_cancelled_orders()

    config = load_config()
    url = "https://vagw-api.eu.prd.portal.restaurant/query"
    
    today = datetime.utcnow()
    print("JOB  STARTED:*** ", today.strftime("%d/%m/%Y %H:%M:%S"))
    # time_from = "2024-10-07T20:00:00.000Z"
    # time_to = "2024-10-08T19:59:59.999Z"
    time_from = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    time_to = today.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "authorization": "Bearer " + config["access_token"],
        "content-length": "816",
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
        "x-country": "AE",
        "x-global-entity-id": "TB_AE",
        "x-request-id": "d9d2e3bd-b986-4cff-b3fe-fd44ef650b0e",
        "x-rps-device": config["deviceUuid"],
        "x-user-id": "2a288f03-5e83-4a66-b398-cfb12002b154",
        "x-vendor-id": config["vendor_id"],
    }

    payload = {
        "operationName": "ListOrders",
        "query": """query ListOrders($params: ListOrdersReq!) {
            orders {
                listOrders(input: $params) {
                    nextPageToken
                    resultTimestamp
                    orders {
                        orderId
                        globalEntityId
                        vendorId
                        vendorName
                        orderStatus
                        placedTimestamp
                        subtotal
                        deliveryType
                    }
                }
            }
        }""",
        "variables": {
            "params": {
                "pagination": {"pageSize": 200},
                "timeFrom": "2025-06-08T20:00:00.000Z",
                "timeTo": "2025-06-10T19:59:59.999Z",
                "globalVendorCodes": [
                    {"globalEntityId": "TB_AE", "vendorId": "663101"},
                    {"globalEntityId": "TB_AE", "vendorId": "716336"}
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print("Error in call first api:",e)

    if response.status_code == 401:
        refresh_access_token()
        return call_first_api()

    api_data = response.json()

    orders = api_data.get('data', {}).get('orders', {}).get('listOrders', {}).get('orders', [])
    if not orders:
        print("No orders found for the given time range.")
        orders = []

    filtered_orders = [order for order in orders if order['orderId'] not in completed_cancelled_orders]

    processed_responses = []
    karama_data = []
    non_karama_data = []
    for order in filtered_orders:
        if order['orderStatus'] in ['completed', 'cancelled']:
            add_order_to_db(order['orderId'], order['orderStatus'])

        #print(order)

        second_api_response = make_second_api_call(order)
        if second_api_response:
            #print(second_api_response)
            formatted_data = format_order_data(second_api_response, order)
            #print("Formatted_dta",formatted_data)
            print(formatted_data['restaurant_id'],"---->")
            if formatted_data['restaurant_id'] == "663101":
                karama_data.append(formatted_data)
            else:
                non_karama_data.append(formatted_data)

    if karama_data:
        final_json = {"data": karama_data}
        send_to_external_api(final_json, 'Karama')
    if non_karama_data:
        final_json = {"data": non_karama_data}
        send_to_external_api(final_json, 'Non Karama')
    """else:
        #print(json.dumps({"data": []}))  # This will print an empty JSON with double quotes
        send_to_external_api({"data": []})"""
        

def make_second_api_call(order):
    config = load_config()
    url = "https://vagw-api.eu.prd.portal.restaurant/query"

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ml;q=0.7",
        "apollographql-client-name": "API Gateway",
        "authorization": "Bearer " + config["access_token"],
        "content-length": "3247",
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
        "x-country": "AE",
        "x-global-entity-id": "TB_AE",
        "x-request-id": "9619b130-076e-46df-b198-cc6a11f87811",
        "x-rps-device": config["deviceUuid"],
        "x-user-id": "2a288f03-5e83-4a66-b398-cfb12002b154",
        "x-vendor-id": config["vendor_id"],
    }

    payload = {
        "operationName": "GetOrderDetails",
        "query": """query GetOrderDetails($params: OrderReq!) {
            orders {
                order(input: $params) {
                    hasBillingData
                    order {
                        orderId
                        placedTimestamp
                        status
                        globalEntityId
                        vendorId
                        vendorName
                        orderValue
                        billableStatus
                        delivery {
                            provider
                            location {
                                AddressText
                                city
                                district
                                postCode
                            }
                        }
                        items {
                            id: productId
                            name
                            quantity
                            unitPrice
                            customerNotes
                        }
                    }
                    orderStatuses {
                        status
                        timestamp
                    }
                    billing {
                        billingStatus
                        estimatedVendorNetRevenue
                        taxTotalAmount
                        inputTax
                        outputTax
                        vendorPayout
                        payment {
                            cashAmountCollectedByVendor
                            paymentType
                            method
                            paymentFee
                        }
                        expense {
                            totalDiscountGross
                            totalDiscount
                            totalVoucher
                            totalVendorDiscount
                            totalVendorVoucher
                            jokerFeeGross
                            commissionAmountGross
                            commissions {
                                type
                                grossAmount
                                rate
                                base
                            }
                            vendorCharges {
                                grossAmount
                                reason
                            }
                        }
                        revenue {
                            totalPlatformDiscount
                            totalPlatformVoucher
                            totalPartnerDiscount
                            totalPartnerVoucher
                            containerChargesGross
                            minimumOrderValueGross
                            deliveryFeeGross
                            tipGross
                            taxCharge
                            vendorRefunds {
                                grossAmount
                                reason
                            }
                        }
                    }
                    previousVersions {
                        changeAt
                        reason
                        orderState {
                            orderValue
                            items {
                                id: productId
                                name
                                quantity
                                unitPrice
                            }
                        }
                    }
                }
            }
        }""",
        "variables": {
            "params": {
                "orderId": order['orderId'],
                "GlobalVendorCode": {
                    "globalEntityId": order['globalEntityId'],
                    "vendorId": order['vendorId']
                },
                "isBillingDataFlagEnabled": True
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve details for order {order['orderId']}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error making second API call for order {order['orderId']}: {e}")
        return None

def convert_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return date_obj.strftime("%Y-%m-%d %H:%M") 

def format_order_data(second_api_response, order):
    order_details = second_api_response['data']['orders']['order']['order']
    
    order_statuses = second_api_response['data']['orders']['order'].get('orderStatuses', [])
    #print(second_api_response['data']['orders']['order']['billing'].keys())
    
    billing = second_api_response['data']['orders']['order'].get('billing', {})

    def get_status_timestamp(statuses, status_name):
        for status in statuses:
            if status['status'] == status_name:
                return convert_date_format(status.get('timestamp', 'N/A'))
        return "N/A"
    def format_order_items(order_items):
        return ','.join([f"{item['quantity']}X{item['name']}" for item in order_items])
    
    order_items = format_order_items(order_details.get('items', []))
    #print(order_details.get('vendorId', 'N/A'))
    return {
        "restaurant_name": order_details.get('vendorName', 'N/A'),
        "order_id": order_details.get('orderId', 'N/A'),
        "restaurant_id": order.get('vendorId', 'N/A'),
        "delivery_type": order_details.get('delivery', {}).get('provider', 'N/A'),
        "payment_type": order_details.get('paymentType', 'N/A'),
        "payment_method": order_details.get('paymentMethod', 'N/A'),
        "order_status": order_details.get('status', 'N/A'),
        "order_received_at": convert_date_format(order.get('placedTimestamp', 'N/A')),
        "accepted_at": get_status_timestamp(order_statuses, "ACCEPTED"),
        "estimated_ready_to_pick_up_time": get_status_timestamp(order_statuses, "ORDER_PREPARED"),
        "ready_to_pick_up_at": get_status_timestamp(order_statuses, "ORDER_PREPARED"),
        "rider_near_pickup_at": get_status_timestamp(order_statuses, "COURIER_NEAR_PICK_UP"),
        "in_delivery_at": get_status_timestamp(order_statuses, "PICKED_UP"),
        "estimated_delivery_time": get_status_timestamp(order_statuses, "ACCEPTED"),
        "delivered_at": get_status_timestamp(order_statuses, "DELIVERED"),
        "cancelled_at": get_status_timestamp(order_statuses, "CANCELLED"),
        "cancellation_reason": order_details.get('cancellationReason', 'N/A'),
        "cancellation_owner": order_details.get('cancellationOwner', 'N/A'),
        "subtotal": order_details.get('orderValue', 0),
        "packaging_charges": order_details.get('packagingCharges', 'N/A'),
        "minimum_order_value_fee": order_details.get('minimumOrderValueFee', 'N/A'),
        "vendor_refunds": order_details.get('vendorRefunds', 'N/A'),
        "tax_charge": billing.get('taxTotalAmount', 'N/A'),
        "payment_fee": billing.get('paymentFee', 'N/A'),
        "discount_funded_by_vendor": billing.get('expense', {}).get('totalVendorDiscount', 'N/A'),
        "voucher_funded_by_vendor": billing.get('expense', {}).get('totalVendorVoucher', 'N/A'),
        "commission": billing.get('expense', {}).get('commissionAmountGross', 'N/A'),
        "vendor_charges": billing.get('expense', {}).get('vendorCharges', 'N/A'),
        "joker_fee": billing.get('expense', {}).get('jokerFeeGross', 'N/A'),
        "is_payable": billing.get('billingStatus', 'N/A'),
        "is_paid": 'PAID' if billing.get('billingStatus') == 'PAID' else 'NOT PAID',
        "estimated_earnings": billing.get('estimatedVendorNetRevenue', 'N/A'),
        "cash_amount_already_collected_by_vendor": 'N/A',#billing.get('payment', {}).get('cashAmountCollectedByVendor', 'N/A'),
        "amount_owed_back_to_talabat": billing.get('amountOwedBackToTalabat', 'N/A'),
        "payout_amount": order.get('orderValue', 'N/A'),
        "talabat_funded_discount": billing.get('revenue', {}).get('totalPlatformDiscount', 'N/A'),
        "talabat_funded_voucher": billing.get('revenue', {}).get('totalPlatformVoucher', 'N/A'),
        "total_discount": billing.get('expense', {}).get('totalDiscount', 'N/A'),
        "total_voucher": round(billing.get('expense', {}).get('totalVoucher', 0) or 0, 1),
        "final_total": order_details.get('orderValue', 0) - round(billing.get('expense', {}).get('totalVoucher', 0) or 0, 1),
        "internal_commission":round((35.2 / 100) * float(order_details.get('orderValue', 0) - round(billing.get('expense', {}).get('totalVoucher', 0) or 0, 1)), 2),
        "final_earning":(order_details.get('orderValue', 0) - round(billing.get('expense', {}).get('totalVoucher', 0) or 0, 1)) - (round((35.2 / 100) * float(order_details.get('orderValue', 0) - round(billing.get('expense', {}).get('totalVoucher', 0) or 0, 1)), 2)),
        "tax_amount": billing.get('taxTotalAmount', 'N/A'),
        "order_items": order_items
    }

def send_to_external_api(data, location):
    try:
        config = load_config()
        url_karama = config["url_karama"]
        url_non_karama = config["url_non_karama"]
        headers = {
            "Content-Type": "application/json"
        }
        print(data)
        
        #if 1:
        if location == "Karama":
            print("Karama", len(data))
            response = requests.post(url_karama, json=data, headers=headers)
        else:
            print("Ras al Khor", len(data))
            response = requests.post(url_non_karama, json=data, headers=headers)
        if response.status_code == 200:
            print("Data successfully sent to external API")
        else:
            print(f"Failed to send data. Status code: {response}")
    except Exception as e:
        print(f"Error sending data to external API: {e}")
