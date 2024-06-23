# Use an official Node.js runtime as a parent image
FROM node:20

# Set the working directory in the container
WORKDIR /sinasuite-dl

# Copy the package.json and pnpm-lock.yaml files
COPY package.json pnpm-lock.yaml /sinasuite-dl/

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install

# Copy the rest of the application code into the container
COPY . /sinasuite-dl

EXPOSE 3000

# Start the React application
CMD ["pnpm", "start"]