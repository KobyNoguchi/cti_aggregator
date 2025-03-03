#!/usr/bin/env python
"""
Simple script to analyze the HTML structure of The Hacker News website
and find the correct selectors for scraping
"""

from bs4 import BeautifulSoup
import os

print("Analyzing The Hacker News HTML")

# Read the downloaded HTML file
html_path = 'thehackernews.html'
if not os.path.exists(html_path):
    print(f"Error: {html_path} not found")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Find all posts
posts = soup.select('.body-post')
print(f"Found {len(posts)} posts with selector '.body-post'")

if posts:
    # Analyze the first post
    post = posts[0]
    
    # Check if we can find the title
    title_elem = post.select_one('h2.home-title')
    if title_elem:
        print(f"Title found: {title_elem.text.strip()}")
    else:
        print("Title element not found with selector 'h2.home-title'")
    
    # Look for link elements
    links = post.select('a')
    print(f"Found {len(links)} links in the first post")
    for i, link in enumerate(links[:3]):  # Show first 3 links
        print(f"Link {i+1}: {link.get('href', 'No href')} - Text: {link.text[:50] if link.text else 'No text'}")
    
    # Check if we can find the date
    date_elem = post.select_one('.item-label')
    if date_elem:
        print(f"Date found: {date_elem.text.strip()}")
    else:
        print("Date element not found with selector '.item-label'")
    
    # Look for alternative date elements
    time_elements = post.select('time')
    if time_elements:
        print(f"Found {len(time_elements)} time elements")
        for i, time_elem in enumerate(time_elements):
            print(f"Time element {i+1}: {time_elem.text.strip()}")
    
    # Check if we can find the summary
    summary_elem = post.select_one('.home-desc')
    if summary_elem:
        print(f"Summary found: {summary_elem.text.strip()[:100]}...")
    else:
        print("Summary element not found with selector '.home-desc'")
    
    # Print the full HTML of the first post for manual inspection
    print("\nFull HTML of the first post (truncated):")
    print(str(post)[:500] + "...")
else:
    print("No posts found!") 