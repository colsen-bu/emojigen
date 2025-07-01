#!/bin/bash

# Discord Emoji Bot Deployment Script for OCI
# This script automates the deployment process on Oracle Cloud Infrastructure

set -e

echo "🚀 Discord Emoji Bot Deployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    sudo apt update -y
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    print_warning "Docker installed. Please log out and log back in, then run this script again."
    exit 0
fi

# Check if user is in docker group
if ! groups $USER | grep &>/dev/null '\bdocker\b'; then
    print_warning "Adding user to docker group..."
    sudo usermod -aG docker $USER
    print_warning "Please log out and log back in, then run this script again."
    exit 0
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual tokens before continuing."
        print_warning "Run: nano .env"
        exit 1
    else
        print_error ".env.example file not found. Please create a .env file with your tokens."
        exit 1
    fi
fi

# Validate environment variables
print_status "Validating environment variables..."
source .env

if [ -z "$DISCORD_BOT_TOKEN" ] || [ "$DISCORD_BOT_TOKEN" = "your_discord_bot_token_here" ]; then
    print_error "DISCORD_BOT_TOKEN is not set or still has default value"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    print_error "OPENAI_API_KEY is not set or still has default value"
    exit 1
fi

print_status "Environment variables validated ✓"

# Build and deploy
print_status "Building Docker image..."
docker-compose build

print_status "Starting the bot..."
docker-compose up -d

# Wait a moment for container to start
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ Bot deployed successfully!"
    print_status "Container status:"
    docker-compose ps
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
    print_status "To restart: docker-compose restart"
else
    print_error "❌ Deployment failed. Check logs:"
    docker-compose logs
    exit 1
fi

# Setup systemd service for auto-start (optional)
read -p "Would you like to set up auto-start on boot? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Setting up systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/discord-emoji-bot.service > /dev/null <<EOF
[Unit]
Description=Discord Emoji Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=$USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable discord-emoji-bot.service
    print_status "✅ Auto-start service enabled!"
fi

print_status "🎉 Deployment complete!"
print_status "Your Discord Emoji Bot is now running in the background."
