#!/bin/bash

# Update apt packages
sudo apt-get update

# Install dependencies
sudo apt-get install -y python3-pip python3-venv nginx

# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/resume-tailor
sudo ln -s /etc/nginx/sites-available/resume-tailor /etc/nginx/sites-enabled
sudo nginx -s reload

# Start the application with Gunicorn
gunicorn --bind 0.0.0.0:8000 run:app