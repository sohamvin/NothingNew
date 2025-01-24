# from sortedcontainers import SortedDict
# from threading import Lock
# from Order import Order
# import json

# class OrderBook:
#     def __init__(self):
#         self.buy_orders = SortedDict(lambda price: -price)  # Descending price for buy
#         self.sell_orders = SortedDict()  # Ascending price for sell
#         # self.lock = Lock()  # To ensure thread safety
#         self.idMap = {

#         }

#     def add_order(self, order: Order):
#         # """Adds an Order object to the order book."""
#         # with self.lock:
#             print("LOCK")
#             order_book = self.buy_orders if order.order_type == "buy" else self.sell_orders
#             if order.price not in order_book:
#                 order_book[order.price] = []
#             order_book[order.price].append(order)
#             self.idMap[order.order_id] = Order

#     def remove_order(self, order_id: str):
#         # """Removes an order from the order book based on order ID and price."""
#         # with self.lock:

#             #If order id is partially completed and is therefore recorder is redis as such
#             #dont allow deletion
#             #else delete
#             #also check if COMPLETE que me order he kya then dont delet
#             price, order_type = self.idMap[order_id].price, self.idMap[order_id].order_type
#             del self.idMap[order_id]
#             order_book = self.buy_orders if order_type == "buy" else self.sell_orders
#             if price in order_book:
#                 # Remove order with matching ID
#                 order_book[price] = [o for o in order_book[price] if o.order_id != order_id]
#                 # Remove price level if no orders remain
#                 if not order_book[price]:
#                     del order_book[price]


#     def get_orders(self, order_type: str):
#         # """Returns all orders of a given type ('buy' or 'sell')."""
#         # with self.lock:
#             order_book = self.buy_orders if order_type == "buy" else self.sell_orders
#             return [(price, [order.__dict__ for order in orders]) for price, orders in order_book.items()]
        
#     def get_highest_buy_price(self):
#         # """Returns the highest buy price or None if no buy orders exist."""
#         # with self.lock:
#             return self.buy_orders.peekitem(0)[0] if self.buy_orders else None

#     def get_lowest_sell_price(self):
#         # """Returns the lowest sell price or None if no sell orders exist."""
#         # with self.lock:
#             return self.sell_orders.peekitem(0)[0] if self.sell_orders else None


from sortedcontainers import SortedDict
from Order import Order

class OrderBook:
    def __init__(self):
        self.buy_orders = SortedDict(lambda price: -price)  # Descending price for buy
        self.sell_orders = SortedDict()  # Ascending price for sell
        self.idMap = {}

    def add_order(self, order: Order):
        order_book = self.buy_orders if order.order_type == "buy" else self.sell_orders
        if order.price not in order_book:
            order_book[order.price] = []
        order_book[order.price].append(order)
        self.idMap[order.order_id] = order  # Store the actual Order object

    def remove_order(self, order_id: str):
        if order_id in self.idMap:
            price, order_type = self.idMap[order_id].price, self.idMap[order_id].order_type
            del self.idMap[order_id]
            order_book = self.buy_orders if order_type == "buy" else self.sell_orders
            if price in order_book:
                order_book[price] = [o for o in order_book[price] if o.order_id != order_id]
                if not order_book[price]:
                    del order_book[price]

    def get_orders(self, order_type: str):
        return [(price, [order.__dict__ for order in orders]) for price, orders in (self.buy_orders if order_type == "buy" else self.sell_orders).items()]
        
    def get_highest_buy_price(self):
        return self.buy_orders.peekitem(0)[0] if self.buy_orders else None

    def get_lowest_sell_price(self):
        return self.sell_orders.peekitem(0)[0] if self.sell_orders else None
