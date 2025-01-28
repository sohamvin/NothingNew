from sortedcontainers import SortedList
from bisect import bisect_left
from OrderTwo import Order

complated_orders = [

]
class OrderManager:
    def __init__(self):
        self.buy_orders = SortedList(key=lambda order: order.price)  # Store buy orders sorted by price
        self.sell_orders = SortedList(key=lambda order: order.price)  # Store sell orders sorted by price
        self.orders_by_id = {}  # For O(1) lookup by ID

    def add_order(self, order: Order):
        self.orders_by_id[order.order_id] = order
        if order.order_type == "buy":
            self.buy_orders.add(order)
        elif order.order_type == "sell":
            self.sell_orders.add(order)

    def remove_order(self, order: Order):
        del self.orders_by_id[order.order_id]
        if order.order_type == "buy":
            self.buy_orders.remove(order)
        elif order.order_type == "sell":
            self.sell_orders.remove(order)



    # Function to calculate weighted average price
    def calculate_weighted_average(self, order_list):
        total_quantity = 0
        weighted_sum = 0

        if order_list:

            for order in order_list:
                total_quantity += order.quantity
                weighted_sum += order.price * order.quantity
        
        else:
            total_quantity = float('inf')
            weighted_sum = 20

        # Avoid division by zero
        if total_quantity == 0:
            return 0

        return (weighted_sum , total_quantity)

    # Wrapper functions for buy and sell orders
    def weighted_average_buy(self):
        return self.calculate_weighted_average(self.buy_orders)

    def weighted_average_sell(self):
        return self.calculate_weighted_average(self.sell_orders)
    

    def remove_order_by_id(self, order_id: str):
        order = self.orders_by_id.get(order_id)  # Use .get() to avoid KeyError
        if order is None:
            print(f"Order with ID {order_id} not found.")
            return

        if order.order_type == "buy":
            self.buy_orders.remove(order)
        elif order.order_type == "sell":
            self.sell_orders.remove(order)

        del self.orders_by_id[order_id]
        print(f"Order with ID {order_id} has been removed.")


    def get_order_by_id(self, order_id: str):
        return self.orders_by_id.get(order_id, None)  # Return None if not found

    


    def delete_an_order(self, order_id: str)-> dict:

        if order_id not in self.orders_by_id:
            return {
                "order_id" : order_id,
                "done" : False
            }
        else:
            order = self.orders_by_id[order_id]
            data = {
                "done" : True,
                "order_id" : order.order_id,
                "shared_you_get" : order.shares_owned,
                "money_you_get": (order.initial_quantity*order.price- order.amount) if order.order_type == "buy" else order.amount
            }
            self.remove_order_by_id(order_id=order_id)

            return data


    def process_incoming_order(self, order: Order):
        array_of_completed_orders = [

        ]

        while True:
            best_order = self.get_best_price(order.price, incoming_buy=(order.order_type == "buy"))

            print(f"\n{order} was matched with {best_order}")
            if best_order != -1:

                matched_price = min(best_order.price, order.price)
                matched_quantity = min(best_order.quantity, order.quantity)
                order.quantity -= matched_quantity
                best_order.quantity -= matched_quantity
                order.transaction.append(
                    {
                        "quantity": matched_quantity,
                        "price" :  matched_price,
                        "with" : best_order.order_id
                    }
                )

                best_order.transaction.append(
                    {
                        "quantity": matched_quantity,
                        "price" :  matched_price,
                        "with" : order.order_id

                    }
                )

                best_order.amount += matched_price*matched_quantity
                order.amount += matched_price*matched_quantity


                if best_order.order_type == "buy":
                    best_order.shares_owned += matched_quantity
                    order.shares_owned -= matched_quantity
                else:
                    order.shares_owned += matched_quantity
                    best_order.shares_owned -= matched_quantity
                    

                if best_order.quantity == 0:
                    # best_order = self.get_average(best_order)
                    best_order.avg = best_order.amount/best_order.initial_quantity
                    self.remove_order(best_order)
                    array_of_completed_orders.append(best_order)
                    # complated_orders.append(best_order)
                
                if order.quantity == 0:
                    order.avg = order.amount/order.initial_quantity
                    # order = self.get_average(order)
                    array_of_completed_orders.append(order)
                    # complated_orders.append(order)
                    return array_of_completed_orders
            else:
                break

        self.add_order(order)

        return array_of_completed_orders


    def print_status_of_books(self):
        print("\n\n\nBuy orders: ")
        for o in self.buy_orders:
            print(o)
        print("\nSell Orders")
        for o in self.sell_orders:
            print(o)
        

    def testing_processor(self, order: Order):
        print(f"Before Processing : {order}")
        self.print_status_of_books()

        self.process_incoming_order(order)

        print(f"\n\n\n\nAfter Processing")
        self.print_status_of_books()

        # time.sleep(23)


    def get_average(self, order: Order)-> Order:
        for objs in order.transaction:
            order.amount += objs["quantity"] * objs["price"]
            order.quantity += objs["quantity"]
        
        order.avg = order.amount/order.quantity

        return order


    def find_closest_elements(self, lst: SortedList, x: float):
        # Use bisect to find the position where x would fit
        prices = [order.price for order in lst]  # Extract prices from orders
        pos = bisect_left(prices, x)
        
        # Initialize variables for lower and higher elements
        lower = None
        higher = None
        
        # Find the closest lower element
        if pos > 0:
            lower = lst[pos - 1]
        
        # Find the closest higher element
        if pos < len(lst):
            higher = lst[pos]
        
        return lower, higher

    def get_best_price(self, price:float, incoming_buy=True)-> Order:
        orders = self.sell_orders if incoming_buy else self.buy_orders
        
        percent = 2 / 100
        
        # Check if the price exists in the orders
        closest_lower, closest_upper = self.find_closest_elements(orders, price)

        l = 1 - percent
        r = 1 + percent

        # For buy orders
        if incoming_buy:
            if closest_upper is not None:
                if closest_lower is not None:
                    return (closest_upper if abs(price - closest_lower.price) > abs(price - closest_upper.price) and price * percent > abs(price - closest_upper.price) 
                            else closest_lower)
                else:
                    return -1 if price * r < closest_upper.price else closest_upper
            else:
                return -1 if closest_lower is None else closest_lower
            
        # For sell orders
        else:
            if closest_lower is not None:
                if closest_upper is not None:
                    return (closest_lower if abs(price - closest_lower.price) < abs(price - closest_upper.price) and abs(price - closest_lower.price) < price * percent 
                            else closest_upper)
                else:
                    return -1 if price * l > closest_lower.price else closest_lower
            else:
                return -1 if closest_upper is None else closest_upper

# # Example usage of OrderManager with SortedList
# order_manager = OrderManager()


# # Generate additional orders
# additional_orders = []

# UPPER_LIMIT = 15
# # LOWER_LIMIT = 4

# orders_arrival = [
#     ( "sell", 278.5, 9), ("sell", 287.4, 18), ("sell", 360.1, 7), ("buy", 52.7, 9), ("buy", 359.6, 20),
#     ("buy", 255.2, 3), ("sell", 245.22, 28), ("sell", 439.22, 4), ("sell", 289.12, 8), ("buy", 239.99, 19), 
#     ("buy", 324.34, 3), ("buy", 356.45, 18), ("buy", 344.23, 23), ("buy", 677.23, 28), ("sell", 356.23, 1)
# ]

# orders_with_ids = [(str(i + 1),) + order for i, order in enumerate(orders_arrival)]


# when_to_delete = {
#     3-1: "2",
#     7-1: "5",
#     10-1: "2",
#     12-1: "7"
    
# }


# deletions = [

# ]


# # Randomly generate 20 more orders
# for i in range(len(orders_with_ids)):  # Starting from 4 to 23 for unique order IDs
#     order_type = orders_with_ids[i][1]
#     quantity = orders_with_ids[i][3]  # Random quantity between 1 and 20
#     price = orders_with_ids[i][2]  # Random price between 250.0 and 400.0
#     company_id = "AAPL"  # Assuming all orders are for the same stock for simplicity

#     additional_orders.append(Order(orders_with_ids[i][0], datetime.now(), order_type, quantity, price, company_id))


# for i, o in enumerate(additional_orders):
#     order_manager.testing_processor(o)
#     if i in when_to_delete:
#         print("\n\n\nBefore deletion: ")
#         order_manager.print_status_of_books()
#         responce = order_manager.delete_an_order(when_to_delete[i])
#         deletions.append(responce)
#         print("\n\nAfter Deletion: \n\n\n")
#         order_manager.print_status_of_books()



# print("\n\n\n\n\n\n\n\n\n\n")
# for o in complated_orders:
#     print("\n",o, "\n" ,o.transaction)



# print("\n\n\n\n\n\n")
# for dels in deletions:
#     print(dels)
