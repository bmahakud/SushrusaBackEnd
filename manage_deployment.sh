#!/bin/bash

# Sushrusa Backend Deployment Management Script
# Usage: ./manage_deployment.sh [start|stop|restart|status|logs]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Virtual environment is not activated. Please activate it first."
        print_status "Run: source venv/bin/activate"
        exit 1
    fi
}

# Function to start the server
start_server() {
    print_header "Starting Sushrusa Backend Server..."
    check_venv
    
    # Check if server is already running
    if pgrep -f gunicorn > /dev/null; then
        print_warning "Server is already running!"
        print_status "Use 'restart' to restart the server or 'stop' to stop it first."
        return 1
    fi
    
    # Start gunicorn server
    print_status "Starting gunicorn server..."
    gunicorn --config gunicorn.conf.py myproject.wsgi:application &
    
    # Wait for server to start
    sleep 3
    
    # Check if server started successfully
    if pgrep -f gunicorn > /dev/null; then
        print_status "✅ Server started successfully!"
        print_status "🌐 Backend URL: http://localhost:8000"
        print_status "📊 Health check: http://localhost:8000/api/auth/health/"
    else
        print_error "❌ Failed to start server"
        return 1
    fi
}

# Function to stop the server
stop_server() {
    print_header "Stopping Sushrusa Backend Server..."
    
    if pgrep -f gunicorn > /dev/null; then
        print_status "Stopping gunicorn processes..."
        pkill -f gunicorn
        sleep 2
        
        if pgrep -f gunicorn > /dev/null; then
            print_warning "Some processes are still running. Force killing..."
            pkill -9 -f gunicorn
        fi
        
        print_status "✅ Server stopped successfully!"
    else
        print_warning "No gunicorn processes found running."
    fi
}

# Function to restart the server
restart_server() {
    print_header "Restarting Sushrusa Backend Server..."
    stop_server
    sleep 2
    start_server
}

# Function to check server status
check_status() {
    print_header "Sushrusa Backend Server Status"
    
    if pgrep -f gunicorn > /dev/null; then
        print_status "✅ Server is RUNNING"
        print_status "🌐 Backend URL: http://localhost:8000"
        print_status "📊 Health check: http://localhost:8000/api/auth/health/"
        
        echo ""
        print_status "Running processes:"
        ps aux | grep gunicorn | grep -v grep
        
        echo ""
        print_status "Port status:"
        netstat -tlnp | grep 8000 || print_warning "Port 8000 not found in netstat"
        
        # Test health endpoint
        echo ""
        print_status "Testing health endpoint..."
        if curl -s http://localhost:8000/api/auth/health/ > /dev/null; then
            print_status "✅ Health endpoint is responding"
        else
            print_warning "⚠️  Health endpoint is not responding"
        fi
    else
        print_error "❌ Server is NOT RUNNING"
        print_status "Use 'start' to start the server"
    fi
}

# Function to show logs
show_logs() {
    print_header "Recent Server Logs"
    
    if pgrep -f gunicorn > /dev/null; then
        print_status "Gunicorn processes are running. Check the terminal where you started the server for logs."
        print_status "Or use: tail -f logs/django.log"
    else
        print_warning "No gunicorn processes found running."
    fi
}

# Function to deploy (full deployment process)
deploy() {
    print_header "Full Deployment Process"
    check_venv
    
    print_status "Pulling latest changes..."
    git pull origin main
    
    print_status "Installing/updating dependencies..."
    pip install -r requirements.txt
    
    print_status "Running migrations..."
    python manage.py migrate
    
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    
    print_status "Creating necessary directories..."
    mkdir -p logs media staticfiles
    
    print_status "Setting permissions..."
    chmod -R 755 staticfiles/ media/
    
    print_status "Restarting server..."
    restart_server
}

# Main script logic
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    deploy)
        deploy
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|deploy}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the gunicorn server"
        echo "  stop    - Stop the gunicorn server"
        echo "  restart - Restart the gunicorn server"
        echo "  status  - Check server status and health"
        echo "  logs    - Show log information"
        echo "  deploy  - Full deployment process (pull, install, migrate, restart)"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the server"
        echo "  $0 status   # Check if server is running"
        echo "  $0 deploy   # Full deployment"
        exit 1
        ;;
esac
