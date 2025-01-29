# Order Book Matching Engine

This project implements a multi-threaded stock market order matching engine using Redis and RabbitMQ for message processing.

## Prerequisites

Before running the system, ensure that you have the following installed:

1. **Redis**
   - Install Redis:
     ```sh
     sudo apt update
     sudo apt install redis-server
     ```
   - Start Redis:
     ```sh
     redis-server
     ```

2. **Docker**
   - Install Docker:
     ```sh
     sudo apt install docker.io
     ```
   - Run RabbitMQ in a Docker container:
     ```sh
     docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
     ```

- **RabbitMQ Dashboard URL:**
  You can access the RabbitMQ management dashboard at the following URL:
  [http://localhost:15672](http://localhost:15672)

  - **Username:** `guest`
  - **Password:** `guest`

With this setup, you can log in to the RabbitMQ management dashboard using the default credentials (`guest`/`guest`).

## Running the Project

To start the order book matching engine, execute the following commands **in order**:

1. **Activate the Environment and Initialize Services**
   ```sh
   ./activate.sh
   ```

2. **Run the Order Processing Engine**
   ```sh
   python3 BombTwo.py
   ```

3. **Monitor and Clean Up Processed Orders**
   ```sh
   python3 CheckDeleteStatTwo.py
   ```

⚠️ **Do not run these scripts in a different order, as it may cause unexpected behavior.**

## Additional Notes
- Ensure that RabbitMQ and Redis are running before executing the scripts.
- The order processing engine (`BombTwo.py`) continuously listens for incoming orders.
- The monitoring script (`CheckDeleteStatTwo.py`) removes processed orders to maintain efficiency.

For any issues, check the logs or restart Redis and RabbitMQ before re-running the scripts.

