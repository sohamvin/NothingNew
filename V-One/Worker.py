import threading
import redis
import json
from Book import OrderBook
from Matching import MatchingEngine
from Order import Order
from testingFN.TestingOrderBook import AppendBook

class Worker(threading.Thread):
    def __init__(self, company_id):
        super().__init__()
        self.company_id = company_id
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book, company_id)

    def run(self):
        queue_name = f"orders_queue_{self.company_id}"
        print(f"Starting worker for {self.company_id}")
        # with open("OBookStatus_" + self.company_id + ".json", 'w') as json_file:
        #     json_file.write("[\n")  # Start of JSON array

        
        while True:
            try:
                # Blocking pop from Redis (timeout can be set)
                order_data = self.redis_client.brpop(queue_name)
                if not order_data:
                    continue
                
                _, data = order_data  # Unpack tuple returned by brpop
                order_dict = json.loads(data)

                if order_dict["action"] == "delete":

                    print(f"Deletion Order received for {self.company_id}: {order_dict}")
                    self.order_book = self.matching_engine.delete_order_two(order_dict["order_id"], order_dict["order_type"], order_dict["price"], timestamp=order_dict["timestamp"])
                    AppendBook(self.order_book, order_dict, self.company_id)
                    continue
                    
                
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
                
                self.order_book = self.matching_engine.process_order(order)
                #Testing Function
                AppendBook(self.order_book, order_dict, self.company_id)
                
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
        # "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
        # "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
        # "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
    ]

    
    workers = start_workers(companies_list)






