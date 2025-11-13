import os
import sys
import time
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

import json
import requests
import smtplib
import brotli

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from data_handler import DataHandler
from custom_logger import Logger


load_dotenv()

class Scraper:
    def __init__(self):
        current_date = datetime.now().date()
        self.date = current_date.strftime("%Y-%m-%d")
        self.load_config()
        self.load_credentials()
        self.data_handler = DataHandler('noon_db', 'orders')
        self.logger = Logger()


    def load_config(self):
        try:
            with open('config.json') as f:
                self.config = json.load(f)
            self.headers = self.config.get('headers', {})
            self.page_count = self.config.get('result_count')
            self.login_url = self.config.get('login_url')
            self.history_url = self.config.get('history_url')
            self.end_point_history = self.config.get('end_point_history')
            self.end_point_current = self.config.get('end_point_current')
            self.excel_file_path = self.config.get('excel_file_location')
            self.data_end_point_al_karama = self.config.get('data_end_point_al_karama')
            self.data_end_point_ras_al_khor = self.config.get('data_end_point_ras_al_khor')

        except Exception as e:
            self.logger.log_error(f"An unexpected error occurred while loading config: {e}")

    def load_credentials(self):
        try:
            self.cred = {}
            self.cred['mail_server'] = os.getenv('MAIL_SERVER')
            self.cred['mail_port'] = int(os.getenv('MAIL_PORT'))
            self.cred['mail_password'] = os.getenv('EMAIL_PWD')
            self.cred['mail_sender'] = os.getenv('MAIL_SENDER')
            self.cred['mail_receiver'] = os.getenv('MAIL_RECEIVER')
            self.cred['site_username'] = os.getenv('SITE_USERNAME')
            self.cred['site_password'] = os.getenv('SITE_PASSWORD')
            self.cred['proxy_ip'] = os.getenv('PROXY_IP')

        except Exception as e:
            self.logger.log_error(f"An unexpected error occurred while loading credentials: {e}")

    def update_cookie(self, cookie):
        try:
            self.config['headers']['cookie'] = cookie
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print("cookie updated...")

        except Exception as e:
            self.logger.log_error(f"An unexpected error occurred while updating cookie: {e}")            

    def send_data(self, data, location):
        try:
            end_point = ""
            if location == "Al Karama":
                #print(data)
                end_point=self.data_end_point_al_karama
                requests.post(self.data_end_point_al_karama, json=json.loads(data), verify=False)
            else:
                
                end_point=self.data_end_point_ras_al_khor
                requests.post(self.data_end_point_ras_al_khor, json=json.loads(data), verify=False)

                            
        except requests.RequestException as e:
            self.logger.log_error(f"Error making POST request to {end_point}: {e}")

    def scrape_data(self):
        try:
            payload = {
                "dateFrom": "2025-06-17",#self.date,#"2025-01-09",#self.date,
                "dateTo": "2025-06-20",#self.date,#"2025-01-09",#self.date,
                "page": 1,
                "limit": self.page_count,
                "searchKey": "",
                "status": ""
            }
            cookie = self.scrape_new_cookie()        
            self.update_cookie(cookie)
            #self.scrape_data()
            u_p = self.end_point_current
            response = requests.post(self.end_point_current, headers=self.headers, data=json.dumps(payload))  
            #response = brotli.decompress(response.content)
            self.process_data_current(response.json())
            
            time.sleep(3)
            

            u_p = self.end_point_history
            response = requests.post(self.end_point_history, headers=self.headers, data=json.dumps(payload))
                        
            self.process_data_history(response.json())

        except Exception as e:
            self.logger.log_error(f"Failed to make POST request: {e}::{u_p}")
            if response.status_code == 404:
                self.logger.log_error(f"Possible expired cookie - getting new cookie")
                cookie = self.scrape_new_cookie()        
                self.update_cookie(cookie)
                self.scrape_data()

    def process_data_history(self, data):
        try:

            print("history")
            print("point 1",len(data))
            current_orders = []
            print(len(data["data"]["orders"]))
            for i in range(len(data["data"]["orders"])):
                details = {}
                print(data["data"]["orders"][i]["orderRef"])
                details["order_number"] = data["data"]["orders"][i]["orderRef"]
                details["order_unique_id"] = data["data"]["orders"][i]["orderNr"]
                details["order_datetime"] = data["data"]["orders"][i]["createdAt"]
                details["order_outlet"] = data["data"]["orders"][i]["outletInfo"]["name"]
                outlet_code = data["data"]["orders"][i]["outletInfo"]["outletCode"]
                if outlet_code in ["RCRCBW3EXG", "PTTKDCG06V", "BRYNTCXUS0", "KRLBFCENQ1", "JCJCS6G5YG", "CLCTPROGYJ", "NRKLRS72TF"]:
                    details["outlet_location"] = "Al Karama"
                else:
                    #print("Ras Al Khor")
                    details["outlet_location"] = "Ras Al Khor"
                details["customer_name"] = data["data"]["orders"][i]["customerInfo"]["name"]
                details["mobile_number"] = data["data"]["orders"][i]["customerInfo"]["phone"]
                details["delivery_address"] = data["data"]["orders"][i]["customerInfo"]["addressStreet"] + ", " + \
                    data["data"]["orders"][i]["customerInfo"]["addressArea"] + \
                    ", " + data["data"]["orders"][i]["customerInfo"]["addressCity"]
                items = ''
                for j in range(len(data["data"]["orders"][i]["menuInfo"]["items"])):
                    value = data["data"]["orders"][i]["menuInfo"]["items"][j]["name"]
                    items = items + ", " + value
                details["items"] = items
                details["order_total"] = data["data"]["orders"][i]["orderSubtotal"]
                details["order_sub_total"] = data["data"]["orders"][i]["orderTotal"]
                details["order_discount_outlet"] = data["data"]["orders"][i]["orderDiscount"]
                details["internal_commission"] = round(float((26.5 / 100) * details["order_sub_total"]), 2)
                details["final_earning"] = round(float(details["order_sub_total"] - details["internal_commission"]), 2)
                details["da_name"] = data["data"]["orders"][i]["daName"]
                details["da_mobile"] = data["data"]["orders"][i]["daPhone"]
                details["orderStatusCode"] = data["data"]["orders"][i]["orderStatusCode"]
                details["inserted_on"] = str(datetime.now())
                details["updated_on"] = str(datetime.now())
                print(data["data"]["orders"][i]["orderRef"],details["order_total"])
                
                detail_values = list(details.values())
                
                existing_order = self.data_handler.retrieve_data(detail_values[1])
                if existing_order is None:#remove condition later
                    self.data_handler.insert_data(detail_values)
                else:
                    if detail_values[-3] != existing_order[-3]:
                        self.data_handler.update_data(detail_values[1], 'da_name', detail_values[-5])
                        self.data_handler.update_data(detail_values[1], 'da_mobile', detail_values[-4])
                        self.data_handler.update_data(detail_values[1], 'orderStatusCode', detail_values[-3])
                #current_orders.append(details)
             #json.dumps(list_of_tuples, indent=4)
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            self.send_data(json.dumps({'data':self.data_handler.retrieve_data_by_location(current_date, "Al Karama")}, indent=4), "Al Karama")
            self.send_data(json.dumps({'data':self.data_handler.retrieve_data_by_location(current_date, "Ras Al Khor")}, indent=4), "Ras Al Khor")
            self.data_handler.export_to_excel(self.excel_file_path)
            self.data_handler.close_connection()
        except Exception as e:
            self.logger.log_error(f"Error processing data1:{str(e)}")
            #self.send_email("Error in getting new cookie data. Process stopped!", str(e))
            self.data_handler.close_connection()
            sys.exit()

    def process_data_current(self, data):
        try:
            current_orders = []
            print("point 2",len(data))
            print(len(data["data"]))
            for i in range(len(data["data"])):
                details = {}
                details["order_number"] = data["data"][i]["orderRef"]
                details["order_unique_id"] = data["data"][i]["orderNr"]
                details["order_datetime"] = data["data"][i]["createdAt"]
                details["order_outlet"] = data["data"][i]["outletInfo"]["name"]
                outlet_code = data["data"][i]["outletInfo"]["outletCode"]
                if outlet_code in ["RCRCBW3EXG", "PTTKDCG06V", "BRYNTCXUS0", "KRLBFCENQ1", "JCJCS6G5YG", "CLCTPROGYJ", "NRKLRS72TF"]:
                    details["outlet_location"] = "Al Karama"
                else:
                    details["outlet_location"] = "Ras Al Khor"

                details["customer_name"] = data["data"][i]["customerInfo"]["name"]
                details["mobile_number"] = data["data"][i]["customerInfo"]["phone"]
                details["delivery_address"] = data["data"][i]["customerInfo"]["addressStreet"] + ", " + \
                    data["data"][i]["customerInfo"]["addressArea"] + \
                    ", " + data["data"][i]["customerInfo"]["addressCity"]
                items = ''
                for j in range(len(data["data"][i]["menuInfo"]["items"])):
                    value = data["data"][i]["menuInfo"]["items"][j]["name"]
                    items = items + ", " + value
                details["items"] = items
                details["order_total"] = data["data"][i]["orderSubtotal"]
                details["order_sub_total"] = data["data"][i]["orderTotal"]
                details["order_discount_outlet"] = data["data"][i]["orderDiscount"]
                details["internal_commission"] = round(float((26.5 / 100) * details["order_sub_total"]), 2)
                details["final_earning"] = round(float(details["order_sub_total"] - details["internal_commission"]), 2)
                details["da_name"] = data["data"][i]["daName"]
                details["da_mobile"] = data["data"][i]["daPhone"]
                details["orderStatusCode"] = data["data"][i]["orderStatusCode"]
                details["inserted_on"] = str(datetime.now())
                details["updated_on"] = str(datetime.now())
                
                detail_values = list(details.values())
                
                existing_order = self.data_handler.retrieve_data(detail_values[1])
                if existing_order is None:
                    self.data_handler.insert_data(detail_values)
                else:
                    if detail_values[-3] != existing_order[-3]:
                        self.data_handler.update_data(detail_values[1], 'orderStatusCode', detail_values[-3])
                #.append(details)
            
        except Exception as e:
            self.logger.log_error(f"Error processing data2:{str(e)}")
            self.send_email("Error in getting new cookie data. Process stopped!", str(e))
            #self.data_handler.close_connection()
            sys.exit()

    def scrape_new_cookie(self):
        try:
            # Set up proxy configuration            
            chrome_options = Options()
            chrome_options.add_argument('--proxy-server=%s' % self.cred['proxy_ip'])
            #chrome_options.add_argument("--headless")
            chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=chrome_options)
            
            driver.get("https://login.noon.partners/en/?domain=https://restaurant-orders.noon.partners/")#self.login_url)
            
            username_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
            username_elem.send_keys(self.cred['site_username'])
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Next']"))
            )
            next_button.click()
            time.sleep(5)

            #"//span[text() = 'Next']"  

            password_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
            password_elem.send_keys(self.cred['site_password'])
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Sign In']"))
            )
            next_button.click()
            time.sleep(5)

            #WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

            driver.get(self.config['history_url'])
            time.sleep(10)

            cookies = driver.get_cookies()
            
            current_url = driver.current_url
            driver.quit()

            formatted_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            #print(formatted_cookies)
            response = requests.head(current_url, cookies=formatted_cookies)

                       
            return response.request.headers['cookie']
        except Exception as e:
            self.logger.log_error(f"Received a 404 error while fetching new cookie.:{str(e)}")
            self.send_email("Error in getting new cookie data. Process stopped!", str(e))
            self.data_handler.close_connection()
            sys.exit()
    
    def send_email(self, subject, message):
        server = None
        try:
            server = smtplib.SMTP(self.cred['mail_server'], self.cred['mail_port'])
            server.set_debuglevel(1)
            server.starttls()
            server.login(self.cred['mail_sender'], self.cred['mail_password'])

            msg = MIMEMultipart()
            msg['From'] = self.cred['mail_sender']
            msg['To'] = self.cred['mail_receiver']
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server.sendmail(self.cred['mail_sender'], self.cred['mail_receiver'], msg.as_string())
        except Exception as e:
            self.logger.log_error(f"Error sending email: {e}")
        finally:
            if server:
                server.quit()
