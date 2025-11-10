# Use the official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /usr/src/app

# Copy dependency files and install them
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'app' directory into the container
# This includes __init__.py, config.py, services/, etc.
COPY app/ ./app/

# Define the command to run the application (executes the __init__.py runner block)
CMD ["flask", "run", "--host=0.0.0.0"]