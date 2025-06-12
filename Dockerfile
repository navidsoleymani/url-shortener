# Use an official lightweight Python image as the base
FROM python:3.12-slim

# --- Environment Configuration ---
# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure output is logged directly (no buffering)
ENV PYTHONUNBUFFERED=1

# --- Set Working Directory ---
WORKDIR /app

# --- Install System Dependencies ---
# Install required build tools and PostgreSQL client headers
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python Dependencies ---
# Copy the dependency file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
COPY . .

# --- Entrypoint/command is defined in docker-compose.yml ---
