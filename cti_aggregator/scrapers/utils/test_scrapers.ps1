# test_scrapers.ps1 - Script to test all intelligence scrapers

Write-Output "Testing all intelligence scrapers..."

# Change to the current script directory
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
cd $ScriptDir

# Make sure Django server is running
$djangoRunning = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health-check/" -Method Get -ErrorAction Stop
    $djangoRunning = $true
    Write-Output "Django server is running."
} catch {
    Write-Output "Django server is not running. Starting it now..."
    Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python manage.py runserver"
    Write-Output "Waiting for Django server to initialize..."
    Start-Sleep -Seconds 10
}

# Run the scraper tests
Write-Output "Running comprehensive tests of all intelligence scrapers..."
cd backend

# Create a simple test script that will run within Django's environment
$testScript = @"
from ioc_scraper.tasks import (
    fetch_cisco_talos_intelligence,
    fetch_microsoft_intelligence,
    fetch_mandiant_intelligence,
    fetch_unit42_intelligence,
    fetch_zscaler_intelligence,
    fetch_dark_reading_intelligence,
    fetch_google_tag_intelligence
)
from ioc_scraper.models import IntelligenceArticle
from django.db.models import Count
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_single_scraper(name, task_func):
    """Run a single scraper and report results"""
    print(f"Testing {name} scraper...")
    
    # Count articles before
    before_count = IntelligenceArticle.objects.filter(source=name).count()
    print(f"  Before: {before_count} articles from {name}")
    
    # Run the scraper
    start_time = datetime.now()
    try:
        result = task_func()
        print(f"  Scraper result: {result}")
    except Exception as e:
        print(f"  Scraper failed with error: {e}")
        return False
    
    # Count articles after
    after_count = IntelligenceArticle.objects.filter(source=name).count()
    print(f"  After: {after_count} articles from {name}")
    
    # Calculate time taken
    time_taken = (datetime.now() - start_time).total_seconds()
    print(f"  Completed in {time_taken:.2f} seconds")
    
    # Report success/failure
    if after_count > before_count:
        print(f"  ✅ SUCCESS: Added {after_count - before_count} new articles")
        return True
    else:
        print(f"  ⚠️ NO NEW ARTICLES: This could be normal if there is no new content")
        return True  # Still consider this a success

# Test all scrapers
scrapers = [
    ("Cisco Talos", fetch_cisco_talos_intelligence),
    ("Microsoft", fetch_microsoft_intelligence),
    ("Mandiant", fetch_mandiant_intelligence),
    ("Palo Alto Unit 42", fetch_unit42_intelligence),
    ("Zscaler", fetch_zscaler_intelligence),
    ("Dark Reading", fetch_dark_reading_intelligence),
    ("Google TAG", fetch_google_tag_intelligence)
]

successes = 0
failures = 0

print("Running intelligence scraper tests...")
for name, task_func in scrapers:
    if run_single_scraper(name, task_func):
        successes += 1
    else:
        failures += 1

print(f"Scraper tests completed: {successes} successful, {failures} failed")

# Show summary of all sources in database
sources = IntelligenceArticle.objects.values('source').annotate(count=Count('source'))
print("Intelligence sources in database:")
for source in sources:
    print(f"  - {source['source']}: {source['count']} articles")

print(f"\nSCRAPER TEST RESULTS: {successes} successful, {failures} failed\n")
"@

# Write the test script to a file
$testScriptPath = "temp_test_scrapers.py"
$testScript | Out-File -FilePath $testScriptPath -Encoding utf8

# Run the test script using Django's shell
python manage.py shell -c "exec(open('$testScriptPath', 'r', encoding='utf-8').read())"

# Clean up
Remove-Item $testScriptPath -Force
cd ..

# If we started Django, let's keep it running for a moment to check results
if (-not $djangoRunning) {
    # Give the user a chance to see the results
    Write-Output "`nPress Enter to exit and stop the Django server..."
    $null = Read-Host
    
    # Find and stop the Django process
    $djangoProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
    foreach ($process in $djangoProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Output "Stopped Django server process with ID $($process.Id)"
        } catch {
            Write-Output "Failed to stop Django server process with ID $($process.Id): $_"
        }
    }
}

Write-Output "Scraper tests completed." 