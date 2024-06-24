# Use an official Python runtime as a parent image
FROM python:3.12-slim

USER root

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    unixodbc \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get remove openjdk-11-jre-headless

# Add Microsoft's GPG key and repository
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl -sSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update the package list and install the ODBC driver for SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Clean up APT when done
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory in the container
WORKDIR /sinasuite-dl

# Install pnpm globally
RUN npm install -g pnpm

## BACKEND

# Copy the requirements file and install dependencies
COPY requirements.txt /sinasuite-dl/requirements.txt
RUN pip install --no-cache-dir -r /sinasuite-dl/requirements.txt

## FRONTEND

# Copy the package.json and pnpm-lock.yaml files
COPY frontend/package.json frontend/pnpm-lock.yaml /sinasuite-dl/frontend/

# Install frontend dependencies
WORKDIR /sinasuite-dl/frontend
RUN pnpm install

# Copy the rest of the application code into the container, excluding node_modules
COPY . /sinasuite-dl

# Copy supervisord configuration
COPY docker/supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# Expose ports
EXPOSE 8080 3000

# Run supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisor.conf"]
