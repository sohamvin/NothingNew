import requests
import random
import uuid
import time

# Define API endpoint
API_URL = "http://127.0.0.1:5000/add_order"

# Ranges for random order data
PRICE_RANGE = (400, 500)  # Random prices between 100 and 500
QUANTITY_RANGE = (1, 50)  # Random quantities between 1 and 50

# Number of orders to bombard
TOTAL_ORDERS = 8000
DELAY = 0.05  # Delay between requests in seconds (optional)

# List of companies
companies = [
    "Google", "Facebook", "Instagram", "Spotify", "Dropbox", 
    "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
    "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
    "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
]


# Generate and send orders
for i in range(TOTAL_ORDERS):
    # Generate a random order
    order = {
        "company_id" :random.choice(companies),
        "order_id": str(uuid.uuid4()),  # Unique order ID
        "time": time.time(),           # Current timestamp
        "order_type": random.choice(["buy", "sell"]),  # Random order type
        "quantity": random.randint(*QUANTITY_RANGE),   # Random quantity
        "price": random.randint(*PRICE_RANGE),         # Random price
    }

    # Send the order to the API
    response = requests.post(API_URL, json=order)

    # Print response status
    if response.status_code == 200:
        print(f"Order {i+1}/{TOTAL_ORDERS} added successfully: {order}")
    else:
        print(f"Failed to add order {i+1}/{TOTAL_ORDERS}: {response.json()}")

    # Optional: Delay to avoid overloading the server
    time.sleep(DELAY)
