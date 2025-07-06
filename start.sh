#!/bin/bash
echo "Starting Jewelry Customization Platform..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
else
    echo "Starting in development mode..."
    
    # Start backend
    echo "Starting Flask backend..."
    python app.py &
    BACKEND_PID=$!
    
    # Start frontend
    echo "Starting React frontend..."
    cd frontend && npm start &
    FRONTEND_PID=$!
    
    echo "Platform running at:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:5000"
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID" INT
    wait
fi
