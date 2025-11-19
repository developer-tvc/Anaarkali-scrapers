# Project Overview  
This project automatically retrieves daily order data from Careem’s admin APIs, enriches each order with detailed information, categorizes them by outlet, and forwards the processed results to external endpoints while managing token refresh and storing completed or cancelled orders locally.

# Project Description  
This project is a small automation service that integrates with Careem’s admin APIs to fetch daily food delivery orders, enrich them with detailed information, and forward structured results to external systems for reporting or downstream processing. Using Python together with the requests library, the application calls Careem’s minimal orders and full order details endpoints, while local configuration and credentials are stored in config.json and a SQLite database is used to track Delivered and Cancelled orders. Supporting tools from the Python standard library such as sqlite3, smtplib, email.mime, json, and datetime are used to manage persistence, email notifications through Gmail SMTP, and time-based token expiry logic.

The execution starts in main.py, which calls call_first_api in api_caller.py to load configuration, build headers, and query Careem’s minimal orders endpoint. api_caller.py filters the result set to only today’s orders that are not already stored as completed, then calls process_second_api to fetch full details for each order and process_second_api_data to normalize the fields into a consistent structure. Orders are grouped by outlet code into Karama and Non Karama categories and then sent in batches to the external URLs defined in config.json. During this flow, database_handler.py is used to read and update the set of completed or cancelled orders, refresh_token.py is invoked when HTTP 401 responses or nearing expiry indicate the access token must be refreshed, and email_notifier.py sends status notifications regarding token refresh outcomes, all coordinated through shared configuration handled by config_loader.py.

# Installation  

Step 1: Clone the repository  
```bash
git clone <repo-url>
cd <project-folder>
```

Step 2: Create and activate a virtual environment  
```bash
python3 -m venv env
source env/bin/activate
```

Step 3: Install dependencies  
```bash
pip install -r requirements.txt
```

# Configuration  
Update the config.json file with the following keys:

- access_token  
- refresh_token  
- scope  
- expire_at  
- deviceUuid  
- gmail_user  
- gmail_password  
- notification_email  
- karama_url  
- ras_al_khor_url  

# How to Run  

Run the full Careem order processing workflow:  
```bash
python main.py
```

Run only the token refresh process:  
```bash
python -m modules.refresh_token
```

# Module Descriptions  

- **main.py**  
  Entry point that executes the complete Careem order processing workflow.

- **modules/api_caller.py**  
  Fetches minimal orders, filters processed ones, retrieves full order details, structures the data, groups them by outlet, and sends them to configured endpoints.

- **modules/config_loader.py**  
  Loads and saves configuration values stored in config.json.

- **modules/database_handler.py**  
  Handles the SQLite database used to store delivered or cancelled order IDs to prevent duplicate processing.

- **modules/email_notifier.py**  
  Sends Gmail-based email notifications when token refresh succeeds or fails.

- **modules/refresh_token.py**  
  Refreshes the Careem access token, updates configuration values, checks expiry, and triggers email notifications.

# Project Structure  
```text
project-root/
  config.json
  main.py
  requirements.txt

  modules/
    api_caller.py
    config_loader.py
    database_handler.py
    email_notifier.py
    refresh_token.py
    __pycache__/
```

# Tools Used  
- Python  
- Python requests module  
- Sqlite3 for database management  
