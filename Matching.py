
import threading
import json
from Order import Order
from Book import OrderBook
import redis
import time

class MatchingEngine:
    def __init__(self, order_book: OrderBook, name : str):
        self.order_book = order_book
        self.lock = threading.Lock()
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0) 
        # self.running = True
        # threading.Thread(target=self.push_order_book_to_redis, daemon=True).start()
        self.name = name

    def delete_key(self, key):
        result = self.redis_client.delete(key)
        if result == 1:
            print(f"Deleted key: {key}")
        else:
            print(f"Key {key} does not exist.")



    def delete_order_two(self, id, order_procedure, price, timestamp = None):
        with self.lock:
            bad_msg = "You are not allowed to delete this order now. It will be completed shortly"
            good_msg = "Your Order Was Canceled"
            data = {
                "allowed" : 0,
                "done" : "Not",
                "message" : bad_msg,
                "id" : id,
                "timestamp" : timestamp,
                "shares_you_can_take_back" : 0,
                "amount_you_get_back" : 0
            }
            #First Check if order is in the book.
            #Since deletion order is always placed after insertion order(and both go to the same queue), 
            #that means that the incoming order must have
            #been placed in the book.
            #so if order is not in order book, it must have been completed and therfore 
            #in the completed queue. 
            #Prevent Order Deletion of order if already in QUEUE for completion. 
            #otherwise return cash and units

            order_book = (
                    self.order_book.sell_orders if order_procedure == "sell" else self.order_book.buy_orders
                )

            if price in order_book:
                new_orders = []
                order = None
                for o in order_book[price]:
                    if o.order_id == id:
                        order = o
                    else:
                        new_orders.append(o)  # Keep this order
                
                # Update the order book with remaining orders
                order_book[price] = new_orders



                if order_procedure == "sell":
                    self.order_book.sell_orders = order_book 
                else:
                    self.order_book.buy_orders = order_book

                #So the new order is not in order book now

                if order != None:
                    data["message"] = good_msg
                    data["allowed"] = int(1),
                    data["done"] = "Yes"

                    if not self.if_key_exists(id):
                        #this means that the order is still in order book
                        #and the order was never executed even partially.
                        #So you can just return everything

                        #Since Order Never completed even a little bit, no
                        #Transfer of shares or anything
                        if order_procedure == "buy":
                            data["amount_you_get_back"] = order.price
                        else:
                            data["shares_you_can_take_back"] = order.quantity
                    else:
                        #This means that order is still in order book and is partially executed
                        ( money_transaced, quantity_exchanged) = self.read_and_get(order.order_id)

                        if order_procedure == "buy":
                            data["amount_you_get_back"] = order.price*order.quantity 
                            data["shares_you_can_take_back"] = quantity_exchanged
                        else:
                        
                            data["amount_you_get_back"] = money_transaced
                            data["shares_you_can_take_back"] = order.quantity

                del order
            
            #Either if No such price is in order book
            #Or if there is no order by given name in order book

            json_data = json.dumps(data, indent=4) 
                 # Assuming best_order is an object
            self.redis_client.lpush("DELETE", json_data)


            return self.order_book
                    

    def read_and_get(self, id):
            array = self.get_array(id)  # Accessing order_id from the dictionary
            self.delete_key(id) 

            money_transaced = 0
            qunatity_exchanged = 0


            for entry in array:
                print(entry)

                entry = json.loads(entry)

                print(entry)             # print(entry)
                money_transaced += float(entry["price"])*float(entry['quantity'])  # Ensure correct key access
                qunatity_exchanged += float(entry["quantity"])  # Ensure correct key access

            return (money_transaced, qunatity_exchanged)

    
            
    def get_array(self, key):
        # Fetch the JSON string from Redis
        json_data = self.redis_client.get(key)
        
        if json_data is None:
            print(f"No data found for key: {key}")
            return []
        
        # Convert JSON string back to an array of dictionaries
        array_of_dicts = json.loads(json_data)
        return array_of_dicts         

    def delete_order(self, id: str, order_procedure: str, price: float, timestamp):
        with self.lock:
            bad_msg = "You are not allowed to delete this order now. It will be completed shortly"
            good_msg = "Your Order Was Canceled"
            data = {
                "allowed" : 0,
                "done" : "Not",
                "message" : bad_msg,
                "id" : id,
                "timestamp" : timestamp
            }
            order_book = (
                    self.order_book.sell_orders if order_procedure == "sell" else self.order_book.buy_orders
                )
            
            #First Check if order is in the book.
            #Since deletion order is always placed later, that means that the incoming order must have
            #been placed in the book.
            #so if order is not in order book, it must have been completed and therfore 
            #in the completed queue. 
            #if order is still in order book, then we check if it was partially executed. 
            #if it was then we dont allow cancelling
            #Otherwise cool
            if price in order_book:

                book_in_order = False
                
                # Create a new list of orders excluding the one to delete
                new_orders = []
                order = None
                for o in order_book[price]:
                    if o.order_id == id:
                        book_in_order = True  # Found the order to delete
                        order = o
                    else:
                        new_orders.append(o)  # Keep this order
                
                # Update the order book with remaining orders
                order_book[price] = new_orders

                if book_in_order:
                    if not self.if_key_exists(id):
                        data["message"] = good_msg
                        data["allowed"] = 1,
                        data["done"] = "Yes"
                    else:
                        order_book[price].append(order)



            json_data = json.dumps(data, indent=4) 
                 # Assuming best_order is an object
            self.redis_client.lpush("DELETE", json_data)


            return self.order_book


            

    def process_order(self, order: Order):
        with self.lock:
            counter_book = (
                self.order_book.sell_orders if order.order_type == "buy" else self.order_book.buy_orders
            )


            while counter_book:
                incoming_buy = True if order.order_type == "buy" else False

                best_price = self.order_book.get_best_price(price=order.price, incoming_buy=incoming_buy)

                # if (order.order_type == "buy" and order.price >= best_price) or (
                #     order.order_type == "sell" and order.price <= best_price
                # ):
                if best_price != -1:
                    best_order = counter_book[best_price][0]
                    matched_quantity = min(order.quantity, best_order.quantity)
                    matched_price = min(order.price, best_order.price)


                    print(f"Matched: {order.order_type} {order.order_id} with {best_order.order_id} for {matched_quantity}")

                    
                    data = {
                            "quantity" : matched_quantity,
                            "price" : matched_price
                        }

                    json_data = json.dumps(data, indent=4) 


                    self.add_to_array(best_order.order_id, json_data)
                    self.add_to_array(order.order_id, json_data)

                    best_order.quantity -= matched_quantity
                    if best_order.quantity == 0:
                        # self.order_book.remove_order(best_order.order_id)
                        counter_book[best_price].pop(0)
                        if not counter_book[best_price]:
                            del counter_book[best_price]
                        
                        self.redis_client.lpush("COMPLETE", json.dumps(best_order.__dict__))  # Assuming best_order is an object

                        

                    # Handle incoming orders quantity update
                    order.quantity -= matched_quantity
                    if order.quantity == 0:
                        self.redis_client.lpush("COMPLETE", json.dumps(order.__dict__))
                        return self.order_book

                else:
                    break
            
            print("Adding to Order Book")
            # If no match, add the new incoming order to the book.
            self.order_book.add_order(order)

            return self.order_book

    
    def if_key_exists(self, key):
        existing_vale = self.redis_client.get(key)

        if existing_vale is None:
            return False
        
        return True

    def add_to_array(self, key, json_object):
    # Check if the key exists
        existing_value = self.redis_client.get(key)
        
        if existing_value is None:
            # Key does not exist, initialize with an empty array
            self.redis_client.set(key, json.dumps([]))
            print(f"Initialized {key} with an empty array.")
        
        # Retrieve the current array
        current_array = json.loads(self.redis_client.get(key))
        
        # Add the new JSON object to the array
        current_array.append(json_object)
        
        # Update the key with the new array
        self.redis_client.set(key, json.dumps(current_array))
        print(f"Added new object to {key}: {json_object} and becomes {current_array}")

