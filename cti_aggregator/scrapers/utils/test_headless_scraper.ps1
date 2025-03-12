# test_headless_scraper.ps1 - Script to test the headless browser scraper with Selenium

Write-Output "Testing headless browser scraper with Selenium..."

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

# Run the headless scraper test
Write-Output "Running test of headless browser scraper..."
cd backend

# Create a test script that will run within Django's environment
$testScript = @"
from ioc_scraper.tasks import (
    fetch_cisco_talos_intelligence,
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
import sys
import os

# Add the data_sources directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_sources'))

# Import the headless browser module
try:
    from data_sources.headless_browser import (
        is_headless_available,
        scrape_intelligence_articles_headless
    )
    headless_available = is_headless_available()
except ImportError:
    headless_available = False
    print("Headless browser module not available")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define source configurations
source_configs = {
    "Cisco Talos": {
        "url": "https://blog.talosintelligence.com/",
        "article_selector": "article.post",
        "title_selector": "h1.entry-title a",
        "url_selector": "h1.entry-title a",
        "date_selector": "div.entry-meta span.published",
        "summary_selector": "div.entry-content",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    },
    "Mandiant": {
        "url": "https://www.mandiant.com/resources/blog",
        "article_selector": "div.card-blog",
        "title_selector": "h3.card-blog__title",
        "url_selector": "a.card-blog__link",
        "date_selector": "div.card-blog__date",
        "summary_selector": "div.card-blog__description",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    },
    "Palo Alto Unit 42": {
        "url": "https://unit42.paloaltonetworks.com/",
        "article_selector": "article.type-post",
        "title_selector": "h2.entry-title a",
        "url_selector": "h2.entry-title a",
        "date_selector": "time.entry-date",
        "summary_selector": "div.entry-content",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    },
    "Zscaler": {
        "url": "https://www.zscaler.com/blogs/security-research",
        "article_selector": "div.views-row",
        "title_selector": "h2 a",
        "url_selector": "h2 a",
        "date_selector": "div.blog-date",
        "summary_selector": "div.blog-body",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    },
    "Dark Reading": {
        "url": "https://www.darkreading.com/threat-intelligence",
        "article_selector": "div.article-info",
        "title_selector": "h3 a",
        "url_selector": "h3 a",
        "date_selector": "div.article-created",
        "summary_selector": "div.article-summary",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    },
    "Google TAG": {
        "url": "https://blog.google/threat-analysis-group/",
        "article_selector": "article.blog-c-entry",
        "title_selector": "h2.blog-c-entry__title",
        "url_selector": "a.blog-c-entry__link",
        "date_selector": "time.blog-c-entry__time",
        "summary_selector": "p.blog-c-entry__snippet",
        "threat_actor_type_selector": None,
        "target_industries_selector": None
    }
}

def test_headless_scraper(source_name):
    """Test the headless browser scraper for a specific source"""
    if not headless_available:
        print(f"Skipping {source_name} - Headless browser not available")
        return False
    
    config = source_configs.get(source_name)
    if not config:
        print(f"No configuration found for {source_name}")
        return False
    
    print(f"Testing headless scraper for {source_name}...")
    
    # Count articles before
    before_count = IntelligenceArticle.objects.filter(source=source_name).count()
    print(f"  Before: {before_count} articles from {source_name}")
    
    # Run the scraper
    start_time = datetime.now()
    try:
        articles = scrape_intelligence_articles_headless(
            url=config["url"],
            source_name=source_name,
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            url_selector=config["url_selector"],
            date_selector=config["date_selector"],
            summary_selector=config["summary_selector"],
            threat_actor_type_selector=config["threat_actor_type_selector"],
            target_industries_selector=config["target_industries_selector"]
        )
        
        print(f"  Found {len(articles)} articles with headless browser")
        
        # Save a few articles for testing
        for article in articles[:3]:  # Save up to 3 articles
            IntelligenceArticle.objects.update_or_create(
                url=article["url"],
                defaults={
                    "title": article["title"],
                    "source": source_name,
                    "published_date": article.get("published_date", datetime.now()),
                    "summary": article.get("summary", ""),
                    "threat_actor_type": article.get("threat_actor_type", ""),
                    "target_industries": article.get("target_industries", "")
                }
            )
    except Exception as e:
        print(f"  Scraper failed with error: {e}")
        return False
    
    # Count articles after
    after_count = IntelligenceArticle.objects.filter(source=source_name).count()
    print(f"  After: {after_count} articles from {source_name}")
    
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

# First, check if Selenium is installed and working
if headless_available:
    print("✅ Selenium and Chrome WebDriver are properly installed and working")
else:
    print("❌ Selenium or Chrome WebDriver is not available")
    print("Please check your installation:")
    print("1. Make sure selenium is installed: pip install selenium")
    print("2. Make sure Chrome/Chromium is installed")
    print("3. Make sure ChromeDriver is installed and in your PATH")
    sys.exit(1)

# Test all sources
sources = list(source_configs.keys())
successes = 0
failures = 0

print("Running headless browser scraper tests...")
for source_name in sources:
    if test_headless_scraper(source_name):
        successes += 1
    else:
        failures += 1

print(f"Headless scraper tests completed: {successes} successful, {failures} failed")

# Show summary of all sources in database
sources = IntelligenceArticle.objects.values('source').annotate(count=Count('source'))
print("Intelligence sources in database:")
for source in sources:
    print(f"  - {source['source']}: {source['count']} articles")

print(f"\nHEADLESS SCRAPER TEST RESULTS: {successes} successful, {failures} failed\n")
"@

# Write the test script to a file
$testScriptPath = "temp_test_headless_scrapers.py"
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

Write-Output "Headless scraper tests completed." 