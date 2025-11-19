# Project Overview
This project automatically retrieves daily order data from Talabat's vendor APIs, enriches each order with detailed information, groups them by outlet location, and forwards the processed results to external endpoints while managing token refresh and storing completed or cancelled orders locally.

# Project Description
This project automates the retrieval and forwarding of daily Talabat orders for a specific vendor. It connects to Talabat’s vendor APIs, fetches all orders for the current day, pulls full order details for each order, and groups them by outlet location (for example, Karama versus other branches). The application is built with Python 3.10 and uses HTTP/GraphQL calls (via requests), a JSON-based configuration file (config.json), and a local SQLite database (orders.db) to track processed orders. Optional Gmail SMTP settings allow the system to send notifications when token refresh fails.

From an execution perspective, the code flow starts at main.py, which calls call_first_api() in modules.api_caller. That function ensures the database table exists, loads processed orders and configuration, fetches the day’s orders from Talabat, refreshes tokens when necessary, and then for each new order fetches detailed data via make_second_api_call(). The details are normalized in format_order_data(), split into Karama and non-Karama groups, and then sent to the configured external endpoints via send_to_external_api(). The internal modules work together through shared configuration (config_loader), token management (refresh_token), persistence (database), and optional email alerts (email_notifier) to provide a reliable, repeatable daily order export pipeline.

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

Step 3: `Install dependencies`
```bash
pip install -r requirements.txt
```

# Configuration
Update the config.json file with the following keys:
- user_id
- access_token
- refresh_token
- device_token
- deviceUuid
- vendor_id
- email
- role
- smtp_server
- smtp_port
- smtp_username
- smtp_password
- notification_email
- url_karama
- url_non_karama
- gmail_user

# How to Run
Run the full Talabat order processing workflow:
```bash
python main.py
```

Run only the token refresh process:
```bash
python -m modules.refresh_token
```

# Module Descriptions
- **main.py**
  Entry point that runs the full Talabat order processing workflow by calling call_first_api.

- **modules/api_caller.py**
  Handles the end-to-end order workflow: fetches daily orders, skips already processed ones, loads full order details, formats them, splits them by location, and sends the results to external endpoints.

- **modules/api_caller.py_bk**
  Backup version of the API calling logic kept as a reference for older payloads or headers.

- **modules/config_loader.py**
  Loads and saves configuration values stored in config.json.

- **modules/database.py**
  Creates and manages the SQLite orders table and stores completed or cancelled order IDs to prevent duplicate processing.

- **modules/email_notifier.py**
  Sends Gmail-based notification emails when token refresh fails, using SMTP settings from config.json.

- **modules/refresh_token.py**
  Refreshes the Talabat access token using the stored refresh token and device token and updates the values in config.json.

- **instructions.txt**
  Notes the intended cron interval, the entry file to run, and the Python version used.

# Project Structure
```text
project-root/
  config.json
  instructions.txt
  main.py
  orders.db
  requirements.txt

  modules/
    api_caller.py
    api_caller.py_bk
    config_loader.py
    database.py
    email_notifier.py
    refresh_token.py
```

# Tools Used
- Python
- Python requests module
