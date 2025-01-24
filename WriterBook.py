# import json
# import redis
# from FileHandler import JsonFileHandler  # Ensure this imports your JsonFileHandler class
# import threading

# class OrderBookWriter(threading.Thread):
#     def __init__(self, id):
#         super().__init__()  # Call the parent class's __init__ method
#         self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
#         self.file_handler = JsonFileHandler(f'order_book_status_{id}.json')  # Initialize JsonFileHandler

#     def run(self):
#         while True:
#             # Blocking pop from the Redis list (with timeout)
#             status_json = self.redis_client.brpop("ORDER_BOOK_STATUS", timeout=5)  # Wait for up to 5 seconds
            
#             if status_json:
#                 _, data = status_json  # Unpack tuple returned by brpop
#                 order_book_status = json.loads(data.decode('utf-8'))  # Decode and parse JSON
                
#                 # Append order book status to the file using JsonFileHandler
#                 self.file_handler.append(order_book_status)  # Assuming append method handles adding correctly
                
#                 print(f"Wrote order book status to file: {order_book_status}")
#             else:
#                 print("No new order book status available.")

# def start_workers(companies):
#     threads = []
    
#     for company in companies:
#         worker_thread = OrderBookWriter(company)
#         worker_thread.start()
#         threads.append(worker_thread)

#     return threads

# # Example usage of the worker
# if __name__ == "__main__":
#     companies_list = [
#         "Google", "Facebook", "Instagram", "Spotify", "Dropbox", 
#         "Reddit", "Netflix", "Pinterest", "Quora", "YouTube"
#     ]
    
#     workers = start_workers(companies_list)



import json
from FileHandler import JsonFileHandler

j = JsonFileHandler('orders.json')
id = "49693ba8-4df3-447a-9065-09fffb944078"
print(j.GetOrderDetailWithId(id))
# print(j.GetElements(id, 'Spotify'))





