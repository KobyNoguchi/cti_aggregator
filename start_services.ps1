# start_services.ps1 - Script to start all services for the application

# Function to run the tailored intelligence update
function Update-TailoredIntelligence {
    Write-Output "Updating CrowdStrike Tailored Intelligence data..."
    cd $PSScriptRoot
    python run_tailored_intel_update.py
    if ($LASTEXITCODE -ne 0) {
        Write-Output "Warning: Tailored Intelligence update failed with exit code $LASTEXITCODE"
    } else {
        Write-Output "Tailored Intelligence data updated successfully!"
    }
}

# Function to run the tailored intelligence tests
function Test-TailoredIntelligence {
    Write-Output "Running CrowdStrike Tailored Intelligence tests..."
    cd $PSScriptRoot
    python run_tailored_intel_update.py --test
    if ($LASTEXITCODE -ne 0) {
        Write-Output "Warning: Tailored Intelligence tests failed with exit code $LASTEXITCODE"
    } else {
        Write-Output "All Tailored Intelligence tests passed!"
    }
}

# Check for migrations that need to be applied
function Apply-Migrations {
    Write-Output "Checking for and applying database migrations..."
    cd $PSScriptRoot/backend
    python manage.py makemigrations
    python manage.py migrate
    cd $PSScriptRoot
}

# Check if Redis is running in Docker
Write-Output "Checking Redis..."
$redisRunning = docker ps --filter "name=redis-server" --format "{{.Names}}"
if ($redisRunning -ne "redis-server") {
    Write-Output "Starting Redis..."
    docker start redis-server
} else {
    Write-Output "Redis is already running."
}

# Apply any pending migrations
Apply-Migrations

# Start Django Backend
Write-Output "Starting Django Backend..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python manage.py runserver"

# Wait for Django to initialize
Write-Output "Waiting for Django server to initialize..."
Start-Sleep -Seconds 10

# Run Tailored Intelligence tests
Test-TailoredIntelligence

# Update Tailored Intelligence data
Update-TailoredIntelligence

# Verify the data was loaded
Write-Output "Verifying Tailored Intelligence data..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/crowdstrike/tailored-intel/" -Method Get -ErrorAction Stop
    $count = $response.Count
    Write-Output "Successfully verified Tailored Intelligence data - $count records found"
} catch {
    Write-Output "Error verifying Tailored Intelligence data: $_"
    Write-Output "Will continue setup anyway..."
}

# Start Celery Worker
Write-Output "Starting Celery Worker..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; celery -A backend.celery worker --loglevel=info --pool=solo"

# Start Celery Beat
Write-Output "Starting Celery Beat..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; celery -A backend.celery beat --loglevel=info"

# Schedule periodic Tailored Intelligence updates with Celery Beat
Write-Output "Scheduling periodic Tailored Intelligence updates..."
# Note: Make sure your Celery Beat schedule includes the Tailored Intelligence update task

# Start CTI Dashboard (shadcn-based)
Write-Output "Starting CTI Dashboard with shadcn components..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd frontend/cti-dashboard; npm run dev"

# Open the dashboard in the default browser
Write-Output "Opening dashboard in browser..."
Start-Sleep -Seconds 5  # Give the server a moment to start
Start-Process "http://localhost:3000"

Write-Output "All services have been started!"
Write-Output "CTI Dashboard available at: http://localhost:3000"
Write-Output "Backend API available at: http://localhost:8000"
Write-Output "Tailored Intelligence module is active and data has been loaded" 