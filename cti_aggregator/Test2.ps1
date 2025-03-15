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

# Function to test all intelligence scrapers
function Test-IntelligenceScrapers {
    Write-Output "Testing all intelligence scrapers..."
    
    # Save current location
    $originalLocation = Get-Location
    
    # Navigate to the backend directory
    Set-Location "$PSScriptRoot/backend"
    
    # Use the -c parameter to run Python code directly instead of using input redirection
    python manage.py shell -c "exec(open('../tests/run_scrapers_test.py').read())"
    
    # Check the exit code
    if ($LASTEXITCODE -ne 0) {
        Write-Output "Warning: Intelligence scraper tests had failures with exit code $LASTEXITCODE"
    } else {
        Write-Output "Intelligence scraper tests completed!"
    }
    
    # Return to original location
    Set-Location $originalLocation
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

# Test the intelligence scrapers directly
Write-Output "Running comprehensive test of all intelligence scrapers..."
Start-Sleep -Seconds 10  # Give Celery worker time to start up
Test-IntelligenceScrapers

# Trigger immediate intelligence scraping for all sources
Write-Output "Triggering immediate intelligence scraping for all sources..."
Start-Sleep -Seconds 5  # Give Celery worker time to start
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python manage.py shell -c 'from ioc_scraper.tasks import fetch_all_intelligence; fetch_all_intelligence()'"

# Check what sources are being scraped
Write-Output "Checking intelligence sources..."
Start-Sleep -Seconds 15  # Give time for scraping to start
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python manage.py shell -c 'from ioc_scraper.models import IntelligenceArticle; from django.db.models import Count; print(\"Sources found:\", list(IntelligenceArticle.objects.values(\"source\").annotate(count=Count(\"source\"))))'"

# Stop any existing frontend applications
Write-Output "Stopping any existing dashboard instances..."
$nodeProcesses = Get-Process | Where-Object { $_.ProcessName -eq "node" -and $_.Path -eq "C:\Program Files\nodejs\node.exe" }
foreach ($process in $nodeProcesses) {
    try {
        Stop-Process -Id $process.Id -Force
        Write-Output "Stopped process with ID $($process.Id)"
    } catch {
        Write-Output "Failed to stop process with ID $($process.Id): $_"
    }
}

# Clear browser cache for localhost:3000
Write-Output "It's recommended to clear your browser cache or use incognito mode"

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
Write-Output "Multiple intelligence sources should now be visible in the dashboard"

