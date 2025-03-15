function Test-IntelligenceScrapers {
    Write-Output "Testing all intelligence scrapers..."
    
    # Store the current location
    $currentLocation = Get-Location
    
    try {
        # Navigate to the backend directory
        Set-Location "$PSScriptRoot/backend"
        
        # Instead of using redirect, read the file content and pass it as a string to python
        $scriptContent = Get-Content -Path "$PSScriptRoot/tests/run_scrapers_test.py" -Raw
        
        # Use piping instead of redirection
        $scriptContent | python manage.py shell
        
        # Check the exit code
        if ($LASTEXITCODE -ne 0) {
            Write-Output "Warning: Intelligence scraper tests had failures with exit code $LASTEXITCODE"
        } else {
            Write-Output "Intelligence scraper tests completed!"
        }
    }
    finally {
        # Always return to the original directory
        Set-Location $currentLocation
    }
}
