from sortedcontainers import SortedDict
from Order import Order
import bisect

class OrderBook:
    def __init__(self):
        self.buy_orders = SortedDict(lambda price: -price)  # Descending price for buy
        self.sell_orders = SortedDict()  # Ascending price for sell
        self.idMap = {} 

    def get_best_price(self, price, incoming_buy=True):
        

        to_search = self.sell_orders if incoming_buy else self.buy_orders
        prices = list(to_search.keys())

        if price in prices:
            return price
        

        if incoming_buy:
            price = price + price*2/100
            pass
        else:
            price = price - price*2/100
            pass

        # Find index where price would fit
        # index = bisect.bisect_left(prices, price)

        # For buy orders, we want the highest price less than or equal to the incoming price
        # if incoming_buy:
        #     if index > 0:
        #         return prices[index-1]  # Return the highest price less than or equal
        #     return -1  # No suitable price found

        # if incoming_buy:
        #     most = -1
        #     for p in prices:



        # else:
        #      least = -1
        #      for p in prices:
        #           if p > price:
        #                least =p
        #      return least




    def add_order(self, order: Order):
        order_book = self.buy_orders if order.order_type == "buy" else self.sell_orders
        if order.price not in order_book:
            order_book[order.price] = []
        order_book[order.price].append(order)
        self.idMap[order.order_id] = order  # Store the actual Order object

    def remove_order(self, order_id: str):
        # Check if the order ID exists in the idMap
        if order_id in self.idMap:
            # Retrieve the corresponding Order object
            order = self.idMap[order_id]
            
            # Check if the order can be deleted (not partially completed)
            # You need to implement logic here to determine if an order is complete or not
            # For example:
            # if order.is_partially_completed() or order.is_complete():
            #     print("Cannot delete a completed or partially completed order.")
            #     return

            price, order_type = order.price, order.order_type
            
            # Remove from idMap
            del self.idMap[order_id]
            
            # Determine which order book to modify
            order_book = self.buy_orders if order_type == "buy" else self.sell_orders
            
            # Remove the specific order from the respective price level
            if price in order_book:
                # Filter out the specific order by ID
                order_book[price] = [o for o in order_book[price] if o.order_id != order_id]
                
                # Remove price level if no orders remain
                if not order_book[price]:
                    del order_book[price]


    def get_orders(self, order_type: str):
        return [(price, [order.__dict__ for order in orders]) for price, orders in (self.buy_orders if order_type == "buy" else self.sell_orders).items()]
        
    def get_highest_buy_price(self):
        return self.buy_orders.peekitem(0)[0] if self.buy_orders else None

    def get_lowest_sell_price(self):
        return self.sell_orders.peekitem(0)[0] if self.sell_orders else None
