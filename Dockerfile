# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader vader_lexicon

# Copy the FastAPI application code into the container
COPY . .
RUN mkdir static

# Command to run the FastAPI application
CMD ["python", "main.py"]
