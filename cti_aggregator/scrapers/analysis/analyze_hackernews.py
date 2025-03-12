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
    
    # Check for links in the post
    links = post.find_all('a')
    print(f"Found {len(links)} links in the first post")
    
    # Check the first link
    if links:
        first_link = links[0]
        print(f"First link: href='{first_link.get('href')}', text='{first_link.text.strip()}'")
    
    # Check for title
    title = post.select_one('h2.home-title')
    if title:
        print(f"Title: '{title.text.strip()}'")
        # Check if title is inside a link
        title_parent = title.parent
        if title_parent.name == 'a':
            print(f"Title parent is a link with href='{title_parent.get('href')}'")
    
    # Check for date elements
    date = post.select_one('.item-label')
    if date:
        print(f"Date (.item-label): '{date.text.strip()}'")
    
    # Check for summary
    summary = post.select_one('.home-desc')
    if summary:
        print(f"Summary (.home-desc): '{summary.text.strip()[:100]}...'")
    
    # Print some of the HTML for manual inspection
    print("\nFirst 500 characters of post HTML:")
    print(str(post)[:500] + "...")
else:
    print("No posts found with .body-post selector") 