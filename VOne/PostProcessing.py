import json
import threading
import time
import redis
from FileHandler import JsonFileHandler

def get_order_keys(java=False):
    if java:
        return {
            "qkey" : "quantity",
            "id" : "orderId",
            "type" : "orderType",
            "company" : "companyId",
            "time" : "time",
            "price" : "price",
            "quantity" : "quantity"
        }
        
    else:
        return {
            "qkey" : "quantity",
            "id" : "order_id",
            "type" : "order_type",
            "company" : "company_id",
            "time" : "time",
            "price" : "price",
            "quantity" : "quantity"
        }
                #     order = Order(
                #     order_id=order_dict['order_id'],
                #     time=order_dict['time'],
                #     order_type=order_dict['order_type'],
                #     quantity=order_dict['quantity'],
                #     price=order_dict['price'],
                #     company_id=order_dict['company_id']
                # )
        pass



class PostProcessor:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.writehandle = JsonFileHandler('orders.json')
        self.del_order_handler = JsonFileHandler('delete_orders.json')

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
        my_keys = get_order_keys(java=False)
        while True:
            # Fetch the most recent order from the "COMPLETE" queue in Redis
            order = self.redis_client.rpop("COMPLETE")
            delete_ord = self.redis_client.rpop("DELETE")

            if delete_ord:
            #                 data = {
            #     "allowed" : False,
            #     "done" : "Not",
            #     "message" : bad_msg,
            #     "id" : id,
            #     "timestamp" : timestamp
            # }
                delete_ord = delete_ord.decode('utf-8')
                
                # Convert JSON string back to a dictionary
                order_dict = json.loads(delete_ord)

                print(f"{order_dict} delete Order was Executed")

                self.del_order_handler.append(order_dict)


            else:
                print("No Delete orders in the queue, waiting...")
            
            if order:

                print("POST PROCESS", order)
                # Decode the order from bytes to string
                order = order.decode('utf-8')
                
                # Convert JSON string back to a dictionary
                order_dict = json.loads(order)
                print("AFTER JSON : ", order_dict)

                # Instantiate file handlers
                writer = self.writehandle
                array = self.get_array(order_dict[my_keys["id"]])  # Accessing order_id from the dictionary

                self.delete_key(order_dict[my_keys["id"]])  # Corrected typo: 'orde_id' to 'order_id'
                
                if not array:
                    print(order_dict[my_keys["id"]])
                    print(f"No matching entries found for order_id={order_dict[my_keys['id']]}.")
                    time.sleep(0.1)  # Wait briefly if no matching entries are found
                    continue

                total = 0
                quantity = 0

                print(array)

                # array = array.decode('utf-8')

                # print(array)

                for entry in array:
                    print(entry)
                    if isinstance(entry, str):  # Decode only if entry is a string
                        entry = json.loads(entry)
                    print(entry)


                    # entry = entry.decode('utf-8')
                    # print(entry)
                    total += float(entry[my_keys["price"]])*float(entry[my_keys["quantity"]])  # Ensure correct key access
                    quantity += float(entry[my_keys['quantity']])  # Ensure correct key access

                json_obj = {
                    "type": order_dict[my_keys["type"]],  # Accessing type from the dictionary
                    "id": order_dict[my_keys["id"]],       # Accessing id from the dictionary
                    "amount": total,
                    "quantity": quantity,
                    "average": total / quantity if quantity != 0 else 0
                }

                print("DONE" , json_obj)

                # Append the new JSON object to the 'orders.json' file
                writer.append(json_obj)

            else:
                # If no order is found, wait briefly before checking again (to reduce CPU usage)
                print("No orders in the queue, waiting...")
                time.sleep(0.1)  # Uncommented this line to avoid busy waiting

p = PostProcessor()
p.postProcess()
