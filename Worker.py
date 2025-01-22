import redis
import json
from celery_config import app
from Matching import MatchingEngine
from Book import OrderBook
from Order import Order

def get_redis_client():
    return redis.StrictRedis(host='localhost', port=6379, db=0)

@app.task
def process_orders(company_id):

    print("INside Woker")
    """
    Celery task to process orders for a specific company.
    """
    redis_client = get_redis_client()
    queue_name = f"orders_queue_{company_id}"
    order_book = OrderBook()  # Company-specific order book
    matching_engine = MatchingEngine(order_book)  # Matching engine for the company

    print(f"Starting worker for company: {company_id}")

    while True:
        order_data = redis_client.rpop(queue_name)
        if order_data:
            order_dict = json.loads(order_data)
            print(f"Order received for company {company_id}: {order_dict}")
            order = Order(
                order_id=order_dict['order_id'],
                time=order_dict['time'],
                order_type=order_dict['order_type'],
                quantity=order_dict['quantity'],
                price=order_dict['price'],
                company_id=order_dict['company_id']
            )
            matching_engine.process_order(order)
            print(f"Processed order for company {company_id}: {order.order_id}")
        else:
            print(f"No orders in the queue for company {company_id}, waiting...")
            break  # Exit after processing all current orders
