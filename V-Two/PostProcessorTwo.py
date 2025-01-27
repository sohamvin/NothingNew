import json
import redis
from FileHandler import JsonFileHandler
import time

class PostProcessor:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.writehandle = JsonFileHandler('orders.json')
        self.del_order_handler = JsonFileHandler('delete_orders.json')
        self.order_batch = []
        self.delete_order_batch = []

    def postProcess(self):
        while True:
            try:
                # Fetch the most recent order from the "COMPLETE" queue
                complete_order_tuple = self.redis_client.brpop("COMPLETE", timeout=1)

                if complete_order_tuple:
                    _, complete_order = complete_order_tuple
                    complete_order = complete_order.decode('utf-8')
                    order_dict = json.loads(complete_order)
                    print(f"Processed COMPLETE Order: {order_dict}")
                    self.order_batch.append(order_dict)

                # Check for DELETE orders similarly
                delete_order_tuple = self.redis_client.brpop("DELETE", timeout=1)
                if delete_order_tuple:
                    _, delete_order = delete_order_tuple
                    delete_order = delete_order.decode('utf-8')
                    delete_order_dict = json.loads(delete_order)
                    print(f"Processed DELETE Order: {delete_order_dict}")
                    self.delete_order_batch.append(delete_order_dict)

                # Write batches to files periodically
                if len(self.order_batch) >= 10:  # Adjust batch size as needed
                    self.writehandle.append(self.order_batch)
                    self.order_batch.clear()

                if len(self.delete_order_batch) >= 10:  # Adjust batch size as needed
                    self.del_order_handler.append(self.delete_order_batch)
                    self.delete_order_batch.clear()

            except Exception as e:
                print(f"An error occurred: {e}")

            time.sleep(0.01)  # Avoid busy waiting

p = PostProcessor()
p.postProcess()
