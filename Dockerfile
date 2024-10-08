# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=run.py

# Start Redis server and run the application with Gunicorn
CMD service redis-server start && gunicorn --bind 0.0.0.0:5000 run:app