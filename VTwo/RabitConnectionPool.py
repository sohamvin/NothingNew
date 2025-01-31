import pika
from queue import Queue
import threading
import time

class RabbitMQConnectionPool:
    def __init__(self, max_connections=5):
        self.pool = Queue(max_connections)  # Limit to 5 connections
        self.lock = threading.Lock()

        for _ in range(max_connections):
            conn = self.create_connection()
            self.pool.put(conn)  # Add connection to the pool

    def create_connection(self):
        """Create a new RabbitMQ connection."""
        return pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', heartbeat=600, blocked_connection_timeout=300)
        )

    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.get()

    def return_connection(self, connection):
        """Return a connection to the pool."""
        self.pool.put(connection)

    def close_all(self):
        """Close all connections when shutting down."""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
