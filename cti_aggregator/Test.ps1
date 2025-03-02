# start_services.ps1 - Script to start all services for the application

# Check if Redis is running in Docker
Write-Output "Checking Redis..."
$redisRunning = docker ps --filter "name=redis-server" --format "{{.Names}}"        
if ($redisRunning -ne "redis-server") {
    Write-Output "Starting Redis..."
    docker start redis-server
} else {
    Write-Output "Redis is already running."
}

# Start Django Backend
Write-Output "Starting Django Backend..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python manage.py runserver"

# Start Celery Worker
Write-Output "Starting Celery Worker..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; celery -A backend.celery worker --loglevel=info --pool=solo"

# Start Celery Beat
Write-Output "Starting Celery Beat..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; celery -A backend.celery beat --loglevel=info"

# Start HeroUI Dashboard
Write-Output "Starting HeroUI Dashboard..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd frontend/my-heroui-dashboard; npm run dev"

# Open the dashboard in the default browser
Write-Output "Opening dashboard in browser..."
Start-Sleep -Seconds 5  # Give the server a moment to start
Start-Process "http://localhost:3000/dashboard"

Write-Output "All services have been started!"
Write-Output "HeroUI Dashboard available at: http://localhost:3000/dashboard"
Write-Output "Backend API available at: http://localhost:8000"
