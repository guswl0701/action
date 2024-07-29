# syntax=docker/dockerfile:1
FROM python:3

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    vim \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    default-mysql-client

# Create code directory
RUN mkdir /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Copy requirements file
COPY requirements.txt /code/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install django-storages boto3 python-dotenv

# Copy project
COPY . /code/

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tickettopia.wsgi:application"]