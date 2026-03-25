#!/bin/bash

# WebSocket Deployment Script for Sushrusa Backend
echo "🚀 Starting WebSocket deployment..."

# Install new dependencies
echo "📦 Installing WebSocket dependencies..."
pip install channels==4.0.0 channels-redis==4.1.0 daphne==4.0.0 redis==5.0.1

# Start Redis if not running
echo "🔴 Starting Redis service..."
if ! docker ps | grep -q sushrusa_redis; then
    echo "Starting Redis container..."
    docker-compose -f docker-compose.redis.yml up -d
    sleep 5
else
    echo "Redis is already running"
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create doctor status records
echo "👨‍⚕️ Creating doctor status records..."
python manage.py create_doctor_statuses

# Test WebSocket connection
echo "🧪 Testing WebSocket connection..."
python -c "
import asyncio
import websockets
import json

async def test_websocket():
    try:
        uri = 'ws://localhost:8000/ws/doctor-status/'
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connection successful')
            await websocket.close()
    except Exception as e:
        print(f'❌ WebSocket connection failed: {e}')

asyncio.run(test_websocket())
"

echo "✅ WebSocket deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Start the server with: python manage.py runserver"
echo "2. For production, use Daphne: daphne -b 0.0.0.0 -p 8000 myproject.asgi:application"
echo "3. Test WebSocket connection at: ws://localhost:8000/ws/doctor-status/"
echo ""
echo "🔗 WebSocket endpoints:"
echo "- Doctor Status: ws://localhost:8000/ws/doctor-status/"
echo "- Notifications: ws://localhost:8000/ws/notifications/"
echo "- Consultations: ws://localhost:8000/ws/consultations/" 