#!/bin/bash

# Sushrusa Backend Deployment Script
echo "🚀 Starting Sushrusa Backend Deployment..."

# Set error handling
set -e

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

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_error "Virtual environment is not activated. Please activate it first."
    exit 1
fi

print_status "Virtual environment is active: $VIRTUAL_ENV"

# Pull latest changes
print_status "Pulling latest changes from git..."
git pull origin main

# Install/update dependencies
print_status "Installing/updating Python dependencies..."
pip install -r requirements.txt

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Set proper permissions
print_status "Setting proper permissions..."
chmod -R 755 staticfiles/
chmod -R 755 media/

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    print_status "Installing gunicorn..."
    pip install gunicorn
fi

# Stop any existing gunicorn processes
print_status "Stopping any existing gunicorn processes..."
pkill -f gunicorn || true

# Wait a moment for processes to stop
sleep 2

# Start gunicorn server
print_status "Starting gunicorn server..."
gunicorn --config gunicorn.conf.py myproject.wsgi:application &

# Wait for server to start
sleep 3

# Check if server is running
if pgrep -f gunicorn > /dev/null; then
    print_status "✅ Server is running successfully!"
    print_status "🌐 Backend URL: http://localhost:8000"
    print_status "📊 Health check: http://localhost:8000/api/auth/health/"
    print_status "📝 Logs: Check the console output for logs"
else
    print_error "❌ Failed to start server"
    exit 1
fi

print_status "🎉 Deployment completed successfully!"

# Show running processes
echo ""
print_status "Running processes:"
ps aux | grep gunicorn | grep -v grep

echo ""
print_status "To stop the server, run: pkill -f gunicorn"
print_status "To view logs, check the console output above"
