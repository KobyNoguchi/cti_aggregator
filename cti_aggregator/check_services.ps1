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

# Start React Frontend
Write-Output "Starting React Frontend..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd frontend; npm start"

Write-Output "All services have been started!"

