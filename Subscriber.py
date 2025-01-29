# import redis
# import json

# class RedisSubscriber:
#     def __init__(self, companies):
#         self.redis_client = redis.Redis(
#             host="localhost",
#             port=6379
#         )
#         self.companies = companies

#     def listen_to_channels(self):
#         # Create a Redis pub/sub instance
#         pubsub = self.redis_client.pubsub()

#         # Subscribe to all company channels
#         pubsub.subscribe(self.companies)

#         print(f"Subscribed to channels: {', '.join(self.companies)}")

#         # Listen for messages
#         for message in pubsub.listen():
#             if message["type"] == "message":
#                 channel = message["channel"]
#                 data = json.loads(message["data"])
#                 print(f"Message received from {channel}: {data}")


# if __name__ == "__main__":
#     companies = [
#         "Google", "Facebook", "Instagram", "Spotify", "Dropbox",
#         # "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
#         # "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
#         # "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
#     ]

#     subscriber = RedisSubscriber(companies)
#     subscriber.listen_to_channels()
