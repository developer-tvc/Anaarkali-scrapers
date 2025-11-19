# Project Overview
This project retrieves daily order information from the Smiles merchant portal, extracts detailed data for each order, stores order statuses locally, and forwards the processed results to an external API endpoint for further use.

# Project Description
This project automates the extraction and transformation of order information from the Eateasily merchant portal. Using Python with requests and BeautifulSoup4, the script logs into the merchant order listing page using predefined cookies and headers, discovers all orders for the current date, and scrapes detailed information for each order including customer, delivery, items, pricing breakdown, and payment details. It then normalizes this data into a consistent structure, stores order status snapshots in a local SQLite database, and prepares a JSON payload suitable for downstream processing by an external REST API.

At runtime, app.py first initializes the orders table in orders.db, then calls extract_arguments() to obtain all relevant order ids from the listing page. For each id, extract_order_details() loads the detail page, parses the HTML into an OrderedDict, and save_order_to_db() persists or updates the order status while preventing updates to completed orders such as Delivered or Cancelled. Once all orders are processed, the script wraps the list of order dictionaries into {"data": [...]} and posts it to external_api_url using requests.post, creating a simple but complete pipeline from web scraping to structured export.

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
Update configuration values inside app.py:
- base_url
- source_url
- cookies
- headers
- DB_NAME
- external_api_url

# How to Run
Run the complete order processing workflow:
```bash
python app.py
```

# Module Descriptions
- **app.py**  
  Main script that fetches order IDs, extracts order details, stores their status, and sends processed data to the external API.

- **orders.db**  
  SQLite database file storing order IDs and statuses to prevent reprocessing of completed orders.

- **logs/smiles.log**  
  Log file containing diagnostic information from previous runs.

- **requirements.txt**  
  Lists Python dependencies required for scraping, parsing, and database handling.

# Project Structure
```text
project-root/
  app.py
  requirements.txt
  orders.db

  logs/
    smiles.log
```

# Tools Used
- Python
- Python requests module
- BeautifulSoup4
