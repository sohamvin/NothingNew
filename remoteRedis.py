import redis

try:
    # Establishing a connection to the Redis server
    redis_client = redis.Redis(
        host='redis-16758.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
        port=16758,
        decode_responses=True,
        username="default",
        password="hTg4EOmVoo4h1OAncK2pAk5RNCFP6XD9",
    )
    
    # Testing the connection by setting a key-value pair
    success = redis_client.set('foo', 'bar')
    
    if success:
        print("Successfully set 'foo' to 'bar'.")

    # Retrieving the value associated with the key 'foo'
    result = redis_client.get('foo')
    
    print(f"The value of 'foo' is: {result}")

except redis.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
