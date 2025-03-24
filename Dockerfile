# Use the official Python 3.9 slim image as base
FROM python:3.9-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (build-essential for compiling packages, libpq-dev if using Postgres, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port on which the app runs
EXPOSE 5000

# Start the Gunicorn server.
# The command "app:create_app()" calls the factory function in app/__init__.py.
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:5000", "--timeout", "300"]
