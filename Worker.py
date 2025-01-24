# import redis
# import json
# from celery_config import app
# from Matching import MatchingEngine
# from Book import OrderBook
# from Order import Order

# def get_redis_client():
#     return redis.StrictRedis(host='localhost', port=6379, db=0)

# @app.task
# def process_orders(company_id):

#     print("INside Woker")
#     """
#     Celery task to process orders for a specific company.
#     """
#     redis_client = get_redis_client()
#     queue_name = f"orders_queue_{company_id}"
#     order_book = OrderBook()  # Company-specific order book
#     matching_engine = MatchingEngine(order_book)  # Matching engine for the company

#     print(f"Starting worker for company: {company_id}")

#     while True:
#         order_data = redis_client.rpop(queue_name)
#         if order_data:
#             order_dict = json.loads(order_data)
#             print(f"Order received for company {company_id}: {order_dict}")
#             order = Order(
#                 order_id=order_dict['order_id'],
#                 time=order_dict['time'],
#                 order_type=order_dict['order_type'],
#                 quantity=order_dict['quantity'],
#                 price=order_dict['price'],
#                 company_id=order_dict['company_id']
#             )
#             matching_engine.process_order(order)
#             print(f"Processed order for company {company_id}: {order.order_id}")
#         else:
#             print(f"No orders in the queue for company {company_id}, waiting...")
#             break  # Exit after processing all current orders


import threading
import redis
import json
from Book import OrderBook
from Matching import MatchingEngine
from Order import Order

class Worker(threading.Thread):
    def __init__(self, company_id):
        super().__init__()
        self.company_id = company_id
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)

    def run(self):
        queue_name = f"orders_queue_{self.company_id}"
        print(f"Starting worker for {self.company_id}")
        
        while True:
            try:
                # Blocking pop from Redis (timeout can be set)
                order_data = self.redis_client.brpop(queue_name)
                if not order_data:
                    continue
                
                _, data = order_data  # Unpack tuple returned by brpop
                order_dict = json.loads(data)
                
                print(f"Order received for {self.company_id}: {order_dict}")
                
                # Create an Order object from received data and process it.
                order = Order(
                    order_id=order_dict['order_id'],
                    time=order_dict['time'],
                    order_type=order_dict['order_type'],
                    quantity=order_dict['quantity'],
                    price=order_dict['price'],
                    company_id=order_dict['company_id']
                )
                
                self.matching_engine.process_order(order)
                
            except Exception as e:
                print(f"Error processing orders for {self.company_id}: {e}")

# Function to start workers for all companies.
def start_workers(companies):
    threads = []
    
    for company in companies:
        worker_thread = Worker(company)
        worker_thread.start()
        threads.append(worker_thread)

    return threads

# Example usage: Start workers for all companies.
if __name__ == "__main__":
    companies_list = [
        "Google", "Facebook", "Instagram", "Spotify", "Dropbox", 
        "Reddit", "Netflix", "Pinterest", "Quora", "YouTube"
    ]
    
    workers = start_workers(companies_list)

