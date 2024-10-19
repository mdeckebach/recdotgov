# Start from a python image
FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Copy source code into working directory
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run the actual script inside Docker
CMD ["python", "./src/main.py"]