# # import threading
# # import time
# # from Order import Order
# # from Book import OrderBook
# # from FileHandler import JsonFileHandler
# # import json

# # class MatchingEngine:
# #     def __init__(self, order_book: OrderBook):
# #         self.order_book = order_book
# #         self.running = True
# #         self.thread = threading.Thread(target=self.run_matching)
# #         self.file_hand = JsonFileHandler('transaction.json')

# #     def start(self):
# #         self.thread.start()

# #     def stop(self):
# #         self.running = False
# #         self.thread.join()

# #     def run_matching(self):
# #         """Continuously match orders from the order book."""
# #         while self.running:
# #             time.sleep(0.1)  # Throttle to avoid high CPU usage

# #     def process_order(self, order: Order):
# #         """
# #         Try to match an order, and if no match is found, add it to the order book.
# #         """
# #         with self.order_book.lock:
# #             # Determine the counter-book
# #             counter_book = (
# #                 self.order_book.sell_orders if order.order_type == "buy" else self.order_book.buy_orders
# #             )

# #             # Try to match the order
# #             while counter_book:
# #                 # Get the best (lowest sell or highest buy) price
# #                 best_price = next(iter(counter_book))
# #                 if (order.order_type == "buy" and order.price >= best_price) or (
# #                     order.order_type == "sell" and order.price <= best_price
# #                 ):
# #                     # Get the best order
# #                     best_order = counter_book[best_price][0]

# #                     # Match quantities
# #                     matched_quantity = min(order.quantity, best_order.quantity)
# #                     print(
# #                         f"Matched: {order.order_type} {order.order_id} with {best_order.order_id} for {matched_quantity}"
# #                     )

# #                     # Update quantities
# #                     order.quantity -= matched_quantity
# #                     best_order.quantity -= matched_quantity

# #                     json_obj = {
# #                         "buyId" : order.order_id if order.order_type == "buy" else best_order.order_id,
# #                         "sellId" : order.order_id if order.order_type == "sell" else best_order.order_id,
# #                         "priceMatch" : min(best_order.price, order.price),
# #                         "quantityMatch" : matched_quantity
# #                     }

# #                     self.file_hand.append(json_obj)

# #                     # Remove fully filled orders
# #                     if best_order.quantity == 0:
# #                         counter_book[best_price].pop(0)
# #                         if not counter_book[best_price]:
# #                             del counter_book[best_price]

# #                     if order.quantity == 0:
# #                         return  # The incoming order is fully filled
# #                 else:
# #                     break  # No match possible

# #             # If no match, add the order to the order book
# #             self.order_book.add_order(order)


# import json
# from Order import Order
# from Book import OrderBook
# from FileHandler import JsonFileHandler
# import redis
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0) 

# class MatchingEngine:
#     def __init__(self, order_book: OrderBook):
#         self.order_book = order_book
#         self.file_hand = JsonFileHandler('transaction.json')

#     def process_order(self, order: Order):
#         # """
#         # Try to match an order, and if no match is found, add it to the order book.
#         # """
#         # with self.order_book.lock:
#             print("IN HERE")
            
#             # Determine the counter-book
#             counter_book = (
#                 self.order_book.sell_orders if order.order_type == "buy" else self.order_book.buy_orders
#             )

#             # Try to match the order
#             while counter_book:
#                 print("IS", order.company_id)
#                 # Get the best (lowest sell or highest buy) price
#                 best_price = next(iter(counter_book))
#                 if (order.order_type == "buy" and order.price >= best_price) or (
#                     order.order_type == "sell" and order.price <= best_price
#                 ):
#                     # Get the best order
#                     best_order = counter_book[best_price][0]

#                     # Match quantities
#                     matched_quantity = min(order.quantity, best_order.quantity)
#                     print(
#                         f"Matched: {order.order_type} {order.order_id} with {best_order.order_id} for {matched_quantity}"
#                     )

#                     # Update quantities
#                     order.quantity -= matched_quantity
#                     best_order.quantity -= matched_quantity

#                     json_obj = {
#                         "buyId": order.order_id if order.order_type == "buy" else best_order.order_id,
#                         "sellId": order.order_id if order.order_type == "sell" else best_order.order_id,
#                         "priceMatch": min(best_order.price, order.price),
#                         "quantityMatch": matched_quantity,
#                     }

#                     self.file_hand.append(json_obj)

#                     # redis_client.set(key = order ids, values = amount traded and for what quantity traded)
#                     #So if the key in the name of an order id is created in redis, 
#                     #then it is not possible to dlete, otherwise dlete from queue, from 

#                     # Remove fully filled orders
#                     if best_order.quantity == 0:
#                         counter_book[best_price].pop(0)
#                         if not counter_book[best_price]:
#                             del counter_book[best_price]
#                         redis_client.lpush("COMPLETE", best_order.order_id)

#                     if order.quantity == 0:
#                         redis_client.lpush("COMPLETE", order.order_id)
#                         return  # The incoming order is fully filled
#                 else:
#                     break  # No match possible
            

#             print("ADDING")
#             # If no match, add the order to the order book
#             self.order_book.add_order(order)

#             print("DONE")


import threading
import json
from Order import Order
from Book import OrderBook
import redis

class MatchingEngine:
    def __init__(self, order_book: OrderBook):
        self.order_book = order_book
        self.lock = threading.Lock()
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0) 
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

                    print(f"Matched: {order.order_type} {order.order_id} with {best_order.order_id} for {matched_quantity}")

                    

                    # Update quantities and handle completed orders
                    best_order.quantity -= matched_quantity
                    if best_order.quantity == 0:
                        counter_book[best_price].pop(0)
                        if not counter_book[best_price]:
                            del counter_book[best_price]
                        
                        self.redis_client.lpush()

                        

                    # Handle incoming orders quantity update
                    order.quantity -= matched_quantity
                    if order.quantity == 0:
                        return

                else:
                    break
            
            print("Adding to Order Book")
            # If no match, add the new incoming order to the book.
            self.order_book.add_order(order)

    
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
        print(f"Added new object to {key}: {json_object}")
