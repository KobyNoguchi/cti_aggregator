import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

# Now we can import Django models
from ioc_scraper.models import IntelligenceArticle

# Get total count
total_count = IntelligenceArticle.objects.count()
print(f"Total intelligence articles: {total_count}")

# Get unique sources
sources = IntelligenceArticle.objects.values_list('source', flat=True).distinct()
print(f"Sources: {list(sources)}")

# Count by source
for source in sources:
    count = IntelligenceArticle.objects.filter(source=source).count()
    print(f"- {source}: {count} articles")

# Get most recent articles
print("\nMost recent articles:")
recent_articles = IntelligenceArticle.objects.order_by('-published_date')[:5]
for article in recent_articles:
    print(f"- {article.title} ({article.source}) - {article.published_date}") 