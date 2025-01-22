import json
import threading
import time
import redis
from FileHandler import JsonFileHandler

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def postProcess():
    while True:
        # Fetch the most recent order ID from the "COMPLETE" queue in Redis
        order_id = redis_client.rpop("COMPLETE")
        
        if order_id:
            print("POST PROCESS", order_id)
            # Decode the order ID from bytes to string
            order_id = order_id.decode('utf-8')
            
            # Instantiate file handlers
            reader = JsonFileHandler('transaction.json')
            writer = JsonFileHandler('orders.json')
            
            # Search for entries corresponding to the order_id
            entries = reader.search(order_id)

            if not entries:
                print(f"No matching entries found for order_id={order_id}.")
                time.sleep(0.1)  # Wait briefly if no matching entries are found
                continue

            total = 0
            quantity = 0

            # Loop through the entries and calculate total and quantity
            for entry in entries:
                total += float(entry["priceMatch"])  # Make sure you access the correct key
                quantity += float(entry["quantityMatch"])  # Make sure you access the correct key

            # Determine if it's a buy or sell order based on the buyId or sellId
            if entries[0].get("buyId") == order_id:
                order_type = "buy"
            else:
                order_type = "sell"

            # Create the JSON object for the result
            json_obj = {
                "type": order_type,
                "id": order_id,
                "amount": total,
                "quantity": quantity,
                "average": total / quantity if quantity != 0 else 0
            }

            # Append the new JSON object to the 'orders.json' file
            writer.append(json_obj)

        else:
            # If no order is found, wait briefly before checking again (to reduce CPU usage)
            print("No orders in the queue, waiting...")
            # time.sleep(0.1)

# Run the worker in a separate thread
# worker_thread = threading.Thread(target=postProcess)

# # Start the worker thread
# worker_thread.daemon = True  # Ensures the thread exits when the main program exits
# worker_thread.start()

# # Main thread will keep running, allowing the worker to continue
# try:
#     while True:
#         time.sleep(1)  # Keep the main thread running
# except KeyboardInterrupt:
#     print("Worker thread interrupted and shutting down...")
#     worker_thread.join()  # Wait for the worker thread to finish


postProcess()
