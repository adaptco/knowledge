FROM node:18-alpine

# Install dependencies
RUN apk add --no-cache bash jq && \
    npm install -g ajv-cli

# Create app directory
WORKDIR /app

# Copy contracts
COPY contracts /app/contracts

# Copy CLI scripts
COPY cli/commands /app/commands
COPY cli/adk.sh /app/adk.sh

# Make scripts executable
RUN chmod +x /app/adk.sh /app/commands/*.sh

# Entrypoint
ENTRYPOINT ["/app/adk.sh"]
