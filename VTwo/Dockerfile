# Use an official Python runtime as a parent image
FROM python:3.9-slim

# RUN apt-get install netstat

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Make port 5672 available to the world outside this container
# EXPOSE 5672

# Ensure the container uses the same network as the RabbitMQ container
# This assumes you have a Docker network named 'orderbook_network'
# Create the network using: docker network create orderbook_network
# Then run the container using: docker run --network orderbook_network -it orderbook_worker_two /bin/bash

# Note: To use the host network, specify the --network host option when running the container.
# This is not recommended for production use due to security concerns
# but is used here to meet the user's requirements.
# For production, consider using proper network configurations.

# Run WorkerTwo.py when the container launches
CMD ["python3", "WorkerTwo.py"]
