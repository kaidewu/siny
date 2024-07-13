# Use an official Node.js runtime as a parent image
FROM node:20

# Set working directory
WORKDIR /frontend

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy all source files
COPY . .

# Build the React application (optional, depending on how you serve it)
RUN pnpm run build

# Start the React application
CMD ["pnpm", "start"]
