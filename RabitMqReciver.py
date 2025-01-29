# import pika
# import redis
# import json


# companies = [
#     "Google", "Facebook", "Instagram", "Spotify", "Dropbox",
#         # "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
#     # "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
#     # "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
# ]

# def process_order(ch, method, properties, body):
#     """
#     Callback function to process messages from RabbitMQ queues.
#     """
#     order = json.loads(body)
#     print(f" [x] Received {order}")
    
#     company_id = order.get("company_id")
#     queue_name = f"orders_queue_{company_id}"
    
#     # Connect to Redis
#     redis_client = redis.Redis(
#         host='redis-16758.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
#         port=16758,
#         decode_responses=True,
#         username="default",
#         password="hTg4EOmVoo4h1OAncK2pAk5RNCFP6XD9",
#     )
    
#     # Handle order based on action type
#     action = order.get("action")
#     if action == "add":
#         print(f"Processing new order for company {company_id}")
#     elif action == "delete":
#         print(f"Processing delete order request for company {company_id}")
#         redis_client.lrem(queue_name, 0, json.dumps(order))  # Remove order from Redis queue
    
#     ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

# # Set up RabbitMQ connection
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()

# # Declare exchange
# exchange_name = 'order_routing'
# channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

# # Subscribe to multiple company queues (you can modify the range based on known company IDs)
# for company_id in companies:  # Adjust range as needed
#     queue_name = f"orders_queue_{company_id}"
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)
#     channel.basic_consume(queue=queue_name, on_message_callback=process_order)
#     print(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")

# # Start consuming messages
# channel.start_consuming()
