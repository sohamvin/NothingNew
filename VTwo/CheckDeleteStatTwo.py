import json
import os
from datetime import datetime

def convert_timestamp_to_readable(timestamp):
    # Convert timestamp to a datetime object
    dt_object = datetime.fromisoformat(timestamp)  # Using ISO format from orders.json
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')


# Get the current working directory
current_path = os.getcwd()

# Load delete_orders.json
with open(os.path.join(current_path, 'delete_orders.json'), 'r') as delete_file:
    delete_orders = json.load(delete_file)

# Load orders.json
with open(os.path.join(current_path, 'orders.json'), 'r') as orders_file:
    orders = json.load(orders_file)

# Load placed_orders.json
with open(os.path.join(current_path, 'placed_orders.json'), 'r') as placed_file:
    placed = json.load(placed_file)

# Load sent_for_deletion.json
with open(os.path.join(current_path, 'sent_for_deletion.json'), 'r') as sent_for_deletion_file:
    sent_for_deletion = json.load(sent_for_deletion_file)

# Check if delete_orders is a list of lists and flatten it if necessary
if isinstance(delete_orders, list) and all(isinstance(sublist, list) for sublist in delete_orders):
    delete_orders = [order for sublist in delete_orders for order in sublist]

# Extract placed order IDs
ids_of_placed = [order['order_id'] for order in placed]

ids_sent_to_be_deleted = [order['order_id'] for order in sent_for_deletion]

# Extract order IDs from delete_orders where done is True
deleted_order_ids = {order['order_id'] for order in delete_orders if order.get('done')}

not_deleted_order_ids = {order['order_id'] for order in delete_orders if not order.get('done')}

# Extract order IDs from orders.json (flattening if necessary)
if isinstance(orders, list) and all(isinstance(sublist, list) for sublist in orders):
    orders = [order for sublist in orders for order in sublist]

order_ids_of_completed_orders = []

for i, o in enumerate(orders):
    order_ids_of_completed_orders.append(o['order_id'])

# print(order_ids_of_completed_orders[0], ids_sent_to_be_deleted[1])

for id in ids_sent_to_be_deleted:
    if id not in deleted_order_ids and id not in not_deleted_order_ids:
        print("SOMETHING IS WRONG HERE FOR : ", id, " It was not deleted or defiend request for it")
        break
    if (id in not_deleted_order_ids and id not in order_ids_of_completed_orders):
        print(id, " Was sent for deletion. its request was denied. but it is not completed")

    if (id in deleted_order_ids and id in order_ids_of_completed_orders):
        print(id, " Was said to have been deleted. But still shows that was completed")
    

    if (id not in not_deleted_order_ids and id not in deleted_order_ids):
        print(id, " Was sent for deletion but no responce for it ever came")

    if (id not in ids_of_placed):
        print("No order with id as ", id, " was even placed. so how come it was requested to be deleted?")
