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

    
    
    
    


# print(ids_of_placed[0])
# deleted_order_ids_list = list(deleted_order_ids)
# if deleted_order_ids_list:  # Check if the list is not empty
#     print("\n\n\n\n", deleted_order_ids_list)
# else:
#     print("\n\n\n\n", "No deleted order IDs available.")

# # Print the first order from orders
# if orders:  # Check if orders list is not empty
#     print("\n\n\n\n", orders[0])
# else:
#     print("\n\n\n\n", "No orders available.")


# for obj in orders

# undeleted_order_ids = [
#     o['order_id']
#     for o in orders
#     if 'order_id' in o
# ]

# # Extract order IDs from delete_orders where done is False, along with additional details
# undeltwo = {
#     order['order_id']: {
#         "timestamp": order.get('timestamp', None),  # Timestamp might not exist
#         "shared_you_get": order.get('shared_you_get', 0), #Set default vals to 0 in no such keys
#         "money_you_get": order.get('money_you_get', 0)
#     }
#     for order in delete_orders if not order.get('done')
# }

# # Initialize lists to store remaining orders that should have been deleted and anomalies
# remaining_orders = []
# wrong = []
# order_not_in_completed_but_placed = []
# order_not_in_deleted_but_placed = []

# # Check for each order in orders.json if it is still present
# for order in undeleted_order_ids:
#     if order in deleted_order_ids:
#         remaining_orders.append(order)

# # Check for placed orders that were not deleted and are not completed
# for placed_order_id in ids_of_placed:
#     if placed_order_id in undeltwo and placed_order_id not in undeleted_order_ids:
#         order_not_in_deleted_but_placed.append(placed_order_id)

# # Check for undeleted orders that should not be present
# for order_id, details in undeltwo.items():
#     if order_id not in undeleted_order_ids:
#         wrong.append({
#             "order_id": order_id,
#             "details": details
#         })

# # Count the number of remaining orders
# remaining_count = len(remaining_orders)

# # Output the results
# print(f"Number of remaining orders that should have been deleted: {remaining_count}")
# print(f"Number of orders whose request for deletion was denied but they are still NOT in completed orders list: {len(wrong)}")

# if remaining_count > 0:
#     print("Remaining orders:")
#     for rem_order in remaining_orders:
#         print(rem_order)

# if len(wrong) > 0:
#     print("Here are the anomalies:")
#     for anomaly in wrong:
#         print(f"Order ID: {anomaly['order_id']}, Timestamp: {convert_timestamp_to_readable(anomaly['details']['timestamp']) if anomaly['details']['timestamp'] else 'N/A'}")

# if len(order_not_in_deleted_but_placed) > 0:
#     print("Orders that were requested for deletion but were not deleted, were placed, and are not completed:")
#     for order_id in order_not_in_deleted_but_placed:
#         print(order_id)
