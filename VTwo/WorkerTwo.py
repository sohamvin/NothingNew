import aio_pika
import asyncio
import json
import time
import dotenv
from BookTwo import OrderManager
import os
dotenv.load_dotenv()
from OrderTwo import Order
import redis
from datetime import datetime


rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')


# Queue names (Each thread listens to one queue)
company_names = os.getenv('COMPANY_NAMES', "Google,Facebook,Instagram,Spotify,Dropbox,Reddit,Netflix,Pinterest,Quora,YouTube,Lyft,Uber,LinkedIn,Slack,Etsy,Mozilla,NASA,IBM,Intel,Microsoft")
companies = company_names.split(',')

map_of_books = {


}

redis_client = None


for company in companies:
    map_of_books[company] = OrderManager()  
    


def connect_redis():
        while True:
            try:
                redis_client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=5)
                redis_client.ping()  # Check connection
                return redis_client
            except redis.ConnectionError:
                print("❌ Redis connection failed, retrying in 5 seconds...")
                time.sleep(5)

connections = []

#Evereything is asynchrounous
async def on_message_received(message: aio_pika.IncomingMessage, channel: aio_pika.Channel, queue_name: str):
    global map_of_books
    global companies
    """Callback function when a message is received."""
    async with message.process():
        message_data = json.loads(message.body)
        action = message_data.get("action")

        # print(f"📥 Received from source: {message_data}")
        exchange = await channel.declare_exchange('complete_delete', aio_pika.ExchangeType.DIRECT)
        complete_queue = await channel.declare_queue("COMPLETE", durable=True)
        delete_queue = await channel.declare_queue("DELETE", durable=True)

        await complete_queue.bind(exchange, routing_key="COMPLETE")
        await delete_queue.bind(exchange, routing_key="DELETE")

        if action == "delete":
            dictionary = map_of_books[queue_name].delete_an_order(message_data["order_id"])
            await exchange.publish(
                aio_pika.Message(body=json.dumps(dictionary).encode('utf-8')),
                routing_key="DELETE"
            )
        else:
            order = Order(
                order_id=message_data["order_id"],
                time=message_data["time"],
                order_type=message_data["order_type"],
                quantity=message_data["quantity"],
                price=message_data["price"],
                company_id=message_data.get("company_id"),
                user_id=message_data["user_id"]
            )

            array = map_of_books[queue_name].process_incoming_order(order=order)
            if array:
                for obj in array:
                    await exchange.publish( 
                        aio_pika.Message(body=json.dumps(obj.__dict__).encode('utf-8')),
                        routing_key="COMPLETE"
                        )

                update_redis(queue_name)

        # print(f"📤 Sent to target queue: {message_data}")


def update_redis(name):
        global map_of_books
        global redis_client
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        (sell_weight, sell_quantity) = map_of_books[name].weighted_average_sell()
        (buy_weight, buy_quantity) = map_of_books[name].weighted_average_buy()
        price = algorithm(sell_weight, buy_weight, sell_quantity, buy_quantity)

        if price > 0:
            data_to_publish = {
                "time": current_time,
                "price": price,
            }
            try:
                redis_client.xadd(name + "_market", data_to_publish)
                response = redis_client.publish(name, json.dumps(data_to_publish))
                # print(f"Response to push was: {response}")

                redis_client.publish(name + "_buy_volume", float(map_of_books[name].total_buy_volume))
                redis_client.publish(name + "_buy_liquid", float(map_of_books[name].total_buy_amount))
                redis_client.publish(name + "_sell_volume", float(map_of_books[name].total_sell_volume))
                redis_client.publish(name + "_sell_liquid", float(map_of_books[name].total_sell_amount))
            except redis.ConnectionError:
                print("❌ Redis connection lost, reconnecting...")
                redis_client = connect_redis()

def algorithm(sell_wt, buy_wt, sell_qt, buy_qt):
        if sell_qt + buy_qt == 0:
            return -1
        return (sell_wt + buy_wt) / (sell_qt + buy_qt)


async def create_connection():
    """Create a new RabbitMQ connection using aio-pika."""
    connection = await aio_pika.connect_robust(
        f'amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/',
    )
    return connection


async def consume_from_queue(queue_name, id: int):
    """Consumer function for a single queue."""
    global connections
    global companies
    # Create a channel for each queue, async
    async with connections[id].channel() as channel:
        qos =  int(os.getenv('QOS', 1)) #This is a reliability to speed tradeoff, more qos is faster but less reliable
        
        await channel.set_qos(prefetch_count=qos)
        queue = await channel.declare_queue(f"orders_queue_{queue_name}" , durable=True)

        # Start consuming messages
        await queue.consume(lambda message: on_message_received(message, channel, queue_name))
        print(f"✅ [Thread-{queue_name}] Listening for messages...")

        # Keep the consumer running
        await asyncio.Future()


async def main():
    """Main function to start consumers."""
    global connections
    global companies
    global redis_client
    redis_client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=5)

    for i in range(int(len(companies)/10)):
        connection = await create_connection()
        connections.append(connection)

    tasks = []
    for j, queue in enumerate(companies):
        task = asyncio.create_task(consume_from_queue(queue, int(j%len(connections))))
        tasks.append(task) 
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("🛑 Stopping consumers...")
        if connection:
            await connection.close()

if __name__ == "__main__":
    asyncio.run(main())





