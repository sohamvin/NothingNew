import requests
import random
import uuid
import time
import json  # Import the json module

# Define API endpoint
API_URL_ADD = "http://127.0.0.1:5000/add_order"
API_URL_DELETE = "http://127.0.0.1:5000/delete_order"  # Assuming you have a delete endpoint

# Ranges for random order data
PRICE_RANGE = (400, 500)  # Random prices between 400 and 500
QUANTITY_RANGE = (1, 50)  # Random quantities between 1 and 50

# Number of orders to bombard
TOTAL_ORDERS = 1000
DELAY = 0.05  # Delay between requests in seconds (optional)

# List of companies
companies = [
    "Google", "Facebook", "Instagram", "Spotify", "Dropbox", 
    # "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
    # "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
    # "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
]

# Store placed orders
placed_orders = []

# Generate and send orders
for i in range(TOTAL_ORDERS):
    # Generate a random order
    order = {
        "company_id": random.choice(companies),
        "order_id": str(uuid.uuid4()),  # Unique order ID
        "time": time.time(),             # Current timestamp
        "order_type": random.choice(["buy", "sell"]),  # Random order type
        "quantity": random.randint(*QUANTITY_RANGE),   # Random quantity
        "price": random.randint(*PRICE_RANGE),         # Random price
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
    if i >= TOTAL_ORDERS // 2:  # Start deleting after half of the orders are placed
        if placed_orders:  # Ensure there are orders to delete
            order_to_delete = random.choice(placed_orders)  # Pick a random order to delete
            
            # Prepare deletion request payload
            delete_payload = {
                "order_id": order_to_delete["order_id"],
                "order_procedure": order_to_delete["order_type"],  # Use the same type for deletion
                "price": order_to_delete["price"],
                "company_id" : order_to_delete["company_id"],
                "timestamp" : order_to_delete["time"]
            }
            
            # Send the deletion request to the API
            delete_response = requests.delete(API_URL_DELETE, json=delete_payload)

            # Print response status for deleting order
            if delete_response.status_code == 200:
                print(f"Deleted Order: {delete_payload}")
                placed_orders.remove(order_to_delete)  # Remove from tracked orders after deletion
            else:
                print(f"Failed to delete order: {delete_response.json()}")

    # Optional: Delay to avoid overloading the server
    time.sleep(DELAY)

# Write placed orders to a JSON file at the end of processing
with open("placed_orders.json", 'w') as json_file:
    json.dump(placed_orders, json_file, indent=4)

print(f"All placed orders have been written to 'placed_orders.json'.")
