from django.db import models

class Vulnerability(models.Model):
    cve_id = models.CharField(max_length=50, unique=True, null=False,default="2000-01-01")
    vulnerability_name = models.CharField(max_length=500)
    description = models.TextField()
    severity = models.CharField(max_length=50)
    published_date = models.DateField()
    source_url = models.URLField()

    def __str__(self):
        return f"{self.cve_id} - {self.vulnerability_name}"

class IntelligenceArticle(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=100)  # Cisco Talos, Microsoft, Mandiant, etc.
    url = models.URLField(unique=True)  # Use URL as unique identifier to avoid duplicates
    published_date = models.DateTimeField()
    summary = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['source']),
            models.Index(fields=['published_date']),
        ]
    
    def __str__(self):
        return f"{self.source}: {self.title}"

class CrowdStrikeIntel(models.Model):
    actor_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    capabilities = models.JSONField(null=True, blank=True)
    motivations = models.JSONField(null=True, blank=True)
    objectives = models.JSONField(null=True, blank=True)
    adversary_type = models.CharField(max_length=100, null=True, blank=True)
    origins = models.JSONField(null=True, blank=True)
    last_update_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
