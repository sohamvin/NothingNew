import json
import threading
import time
import redis
from FileHandler import JsonFileHandler




class PostProcessor:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.writehandle = JsonFileHandler('orders.json')

    def get_array(self, key):
        # Fetch the JSON string from Redis
        json_data = self.redis_client.get(key)
        
        if json_data is None:
            print(f"No data found for key: {key}")
            return []
        
        # Convert JSON string back to an array of dictionaries
        array_of_dicts = json.loads(json_data)
        return array_of_dicts

    def delete_key(self, key):
        result = self.redis_client.delete(key)
        if result == 1:
            print(f"Deleted key: {key}")
        else:
            print(f"Key {key} does not exist.")

    def postProcess(self):
        while True:
            # Fetch the most recent order ID from the "COMPLETE" queue in Redis
            order = self.redis_client.rpop("COMPLETE")
            
            if order:
                print("POST PROCESS", order)
                # Decode the order ID from bytes to string
                order = order.decode('utf-8')
                
                # Instantiate file handlers
                # reader = JsonFileHandler('transaction.json')
                writer = self.writehandle
                array = self.get_array(order.order_id)

                self.delete_key(order.orde_id)
                
                # Search for entries corresponding to the order_id
                # entries = reader.search(order_id)

                if not array:
                    print(f"No matching entries found for order_id={order.order_id}.")
                    time.sleep(0.1)  # Wait briefly if no matching entries are found
                    continue

                total = 0
                quantity = 0

                for entry in array:
                    total += float(entry["price"])  # Make sure you access the correct key
                    quantity += float(entry["quantity"])  # Make sure you access the correct key


                json_obj = {
                    "type": order.order_type,
                    "id": order.order_id,
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

p = PostProcessor()
p.postProcess()
