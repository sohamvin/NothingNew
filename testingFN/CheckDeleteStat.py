import json
from datetime import datetime

def convert_timestamp_to_readable(timestamp):
    # Convert timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)
    # Format it as a string (you can customize the format as needed)
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')


# Load delete_orders.json
with open('/home/soham/Documents/OrderBook/delete_orders.json', 'r') as delete_file:
    delete_orders = json.load(delete_file)

# Load orders.json
with open('/home/soham/Documents/OrderBook/orders.json', 'r') as orders_file:
    orders = json.load(orders_file)

# Load placed_orders.json
with open('/home/soham/Documents/OrderBook/placed_orders.json', 'r') as placed_file:
    placed = json.load(placed_file)

ids_of_placed = [order['order_id'] for order in placed]

# Extract order IDs from delete_orders where done is "Yes"
deleted_order_ids = {order['id'] for order in delete_orders if order['done'] == "Yes"}

# Extract order IDs from orders.json
undeleted_order_ids = [order['id'] for order in orders]

# Extract order IDs from delete_orders where done is "Not" along with their timestamps
undeltwo = {order['id']: order['timestamp'] for order in delete_orders if order['done'] == "Not"}

# Initialize lists to store remaining orders that should have been deleted and anomalies
remaining_orders = []
wrong = []
order_not_in_completed_but_placed = []
order_not_in_deleted_but_placed = []

# Check for each order in orders.json if it is still present
for order in orders:
    if order['id'] in deleted_order_ids:
        remaining_orders.append(order)

# Check for placed orders that were not deleted and are not completed
for placed_order_id in ids_of_placed:
    if placed_order_id in undeltwo and placed_order_id not in undeleted_order_ids:
        # If the order was requested for deletion but is not completed and was placed
        order_not_in_deleted_but_placed.append(placed_order_id)

# Check for undeleted orders that should not be present
for order_id, timestamp in undeltwo.items():
    if order_id not in undeleted_order_ids:
        wrong.append({
            "id": order_id,
            "timestamp": timestamp
        })

# Count the number of remaining orders
remaining_count = len(remaining_orders)

# Output the results
print(f"Number of remaining orders that should have been deleted: {remaining_count}")
print(f"Number of orders whose request for deletion was denied but they are still NOT in completed orders list: {len(wrong)}")

if remaining_count > 0:
    print("Remaining orders:")
    for rem_order in remaining_orders:
        print(rem_order)

if len(wrong) > 0:
    print("Here are the anomalies:")
    for anomaly in wrong:
        print(anomaly['id'], "\t\t", convert_timestamp_to_readable(anomaly['timestamp']))

if len(order_not_in_deleted_but_placed) > 0:
    print("Orders that were requested for deletion but were not deleted, were placed, and are not completed:")
    for order_id in order_not_in_deleted_but_placed:
        print(order_id)
