"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-16758.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=16758,
    decode_responses=True,
    username="default",
    password="hTg4EOmVoo4h1OAncK2pAk5RNCFP6XD9",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

