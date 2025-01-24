
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

    def process_order(self, order: Order):
        with self.lock:
            counter_book = (
                self.order_book.sell_orders if order.order_type == "buy" else self.order_book.buy_orders
            )

            while counter_book:
                best_price = next(iter(counter_book))
                if (order.order_type == "buy" and order.price >= best_price) or (
                    order.order_type == "sell" and order.price <= best_price
                ):
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

    # def push_order_book_to_redis(self):
    #     while self.running:
    #         time.sleep(10)  # Wait for 10 seconds
    #         order_book_status = {
    #             "name" : self.name,
    #             "buy_orders": self.order_book.buy_orders,
    #             "sell_orders": self.order_book.sell_orders,
    #             "timestamp": time.time()
    #         }
    #         self.redis_client.lpush("ORDER_BOOK_STATUS", json.dumps(order_book_status))
    #         print("Pushed order book status to Redis.")

    # def stop(self):
    #     self.running = False
