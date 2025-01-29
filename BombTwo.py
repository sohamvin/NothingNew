import requests
import random
import uuid
import time
from datetime import datetime, timedelta, timezone
import json

PORT = 8935
# Define API endpoint
API_URL_ADD = f"http://127.0.0.1:{PORT}/add_order"
API_URL_DELETE = f"http://127.0.0.1:{PORT}/delete_order"

# Ranges for random order data
PRICE_RANGE = (400, 500)
QUANTITY_RANGE = (1, 50)

# Number of orders to bombard
TOTAL_ORDERS = 500
DELAY = 0.05

# List of companies
companies = [
    "Google", "Facebook", "Instagram", "Spotify", "Dropbox",
        "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
    "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
    "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
]

# Store placed orders
placed_orders = []
sent_for_deletion = []




# Timezone setup for IST
ist = timezone(timedelta(hours=5, minutes=30))

# Generate and send orders
for i in range(TOTAL_ORDERS):
    # Generate a random order
    order = {
        # "action" : "add",
        "order_id": str(uuid.uuid4()),
        "time": str(datetime.now(ist).isoformat()),  # Current time in ISO format with IST timezone
        "order_type": random.choice(["buy", "sell"]),
        "quantity": random.randint(*QUANTITY_RANGE),
        "price": random.randint(*PRICE_RANGE),
        "company_id": random.choice(companies),
        "user_id" : str(uuid.uuid4())
    }

    # Send the order to the API
    response = requests.post(API_URL_ADD, json=order)

    # Print response status for adding order
    if response.status_code == 200:
        print(f"Order {i + 1}/{TOTAL_ORDERS} added successfully: {order}")
        placed_orders.append(order)  # Keep track of the placed order
    else:
        print(f"Failed to add order {i + 1}/{TOTAL_ORDERS}: {response.json()}")

    # Randomly decide to delete an order after some orders have been placed
    if i >= TOTAL_ORDERS // 2:
        if placed_orders:
            order_to_delete = random.choice(placed_orders)

            # Prepare deletion request payload
            delete_payload = {
                "action" : "delete",
                "order_id": order_to_delete["order_id"],
                "order_procedure": order_to_delete["order_type"],
                "price": order_to_delete["price"],
                "company_id": order_to_delete["company_id"],
                "time": order_to_delete["time"],
            }

            print("My Delete Payload:", delete_payload)

            # Send the deletion request to the API
            delete_response = requests.delete(API_URL_DELETE, json=delete_payload)

            # Print response status for deleting order
            if delete_response.status_code == 200:
                print(f"Deleted Order: {delete_payload}")
                sent_for_deletion.append(order_to_delete)
                index_to_delete = placed_orders.index(order_to_delete)
                removed_order = placed_orders.pop(index_to_delete)
            else:
                print(f"Failed to delete order: {delete_response.json()}")

    # Optional: Delay to avoid overloading the server
    time.sleep(DELAY)

# # Write placed orders and completed orders to a JSON file
# with open("placed_orders.json", 'w') as json_file:
#     json.dump(placed_orders + sent_for_deletion, json_file, indent=4)

# with open("sent_for_deletion.json", 'w') as js_file:
#     json.dump(sent_for_deletion, js_file, indent=4)

# print(f"All placed orders have been written to 'placed_orders.json'.")
