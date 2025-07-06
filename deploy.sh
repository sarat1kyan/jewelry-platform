#!/bin/bash
echo "Deploying Jewelry Customization Platform..."

# Check configuration
if grep -q "YOUR_MONDAY_API_KEY_HERE" config.ini; then
    echo "WARNING: Please update Monday.com credentials in config.ini"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build and start with Docker Compose
docker-compose build
docker-compose up -d

echo "Deployment complete!"
echo "Access the platform at: http://localhost:3000"
