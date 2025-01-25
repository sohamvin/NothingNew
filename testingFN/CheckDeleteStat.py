import json
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

# Extract order IDs from delete_orders where done is "Yes"
deleted_order_ids = {order['id'] for order in delete_orders if order['done'] == "Yes"}

# Extract order IDs from orders.json
undeleted_order_ids = [order['id'] for order in orders]

# Extract order IDs from delete_orders where done is "Not" along with their timestamps
undeltwo = {order['id']: order['timestamp'] for order in delete_orders if order['done'] == "Not"}

# Initialize a list to store remaining orders that should have been deleted
remaining_orders = []
wrong = []

# Check for each order in orders.json if it is still present
for order in orders:
    if order['id'] in deleted_order_ids:
        remaining_orders.append(order)



print(undeleted_order_ids)

# Check for undeleted orders that should not be present
for order_id, timestamp in undeltwo.items():
    if order_id not in undeleted_order_ids:
        print(order_id)
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
        print(anomaly['id'], "\t\t" ,convert_timestamp_to_readable(anomaly['timestamp']))

# Load delete_orders.json
# with open('delete_orders.json', 'r') as delete_file:
#     delete_orders = json.load(delete_file)

# # Load orders.json
# with open('orders.json', 'r') as orders_file:
#     orders = json.load(orders_file)

# # Convert timestamps in delete_orders.json
# for order in delete_orders:
#     order['readable_time'] = convert_timestamp_to_readable(order['timestamp'])

# # Convert timestamps in orders.json
# for order in orders:
#     if 'time' in order:  # Check if 'time' key exists
#         order['readable_time'] = convert_timestamp_to_readable(order['time'])
#     else:
#         order['readable_time'] = "N/A"  # Handle missing time gracefully
