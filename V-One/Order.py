from datetime import datetime, timedelta, timezone

class Order:
    def __init__(self, order_id: str, time: datetime, order_type: str, quantity: int, price: float, company_id: str, user_id: str = None):
        # Create a timezone for IST (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        
        self.order_id = order_id
        # Ensure time is in IST
        if time.tzinfo is None:
            self.time = time.replace(tzinfo=ist)  # Assuming time is naive
        else:
            self.time = time.astimezone(ist)  # Convert to IST if already timezone-aware
        
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.company_id = company_id
        self.user_id = user_id

        self.transactions = [
            #{
                #quantity:
                #price:
                #with order_id:
            #}
        ]

    def __del__(self):
        print('Destructor called, Order deleted.')
