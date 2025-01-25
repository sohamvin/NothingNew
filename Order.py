
class Order:
    def __init__(self, order_id, time, order_type, quantity, price, company_id):
        self.order_id = order_id
        self.time = time
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.company_id = company_id

    def __del__(self):
        print('Destructor called, Order deleted.')

