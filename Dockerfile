FROM python:3.11-slim

# Install git (needed for some pip packages)
RUN apt-get update && apt-get install -y git && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install pip and project dependencies
RUN python -m pip install --upgrade pip \
    && pip install -e .

# Set environment variables
ENV ROMAN_SENATE_TEST_MODE=true

# Create an entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]