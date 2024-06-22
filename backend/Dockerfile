# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables to non-interactive for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    unixodbc

# Add Microsoft's GPG key and repository
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl -sSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update the package list and install the ODBC driver for SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory in the container
WORKDIR /sinasuite-dl

# Copy the requirements file into the container at /app
COPY ./requirements.txt /sinasuite-dl/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /sinasuite-dl/requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /sinasuite-dl/

# Run the application
CMD ["python", "main.py"]