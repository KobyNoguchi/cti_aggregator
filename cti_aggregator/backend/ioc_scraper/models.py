from django.db import models
from django.db.models import Index

# TODO: Consider consolidating Vulnerability and CISAKev models
# There is significant overlap between these models, and they could be merged
# into a single model with a source field to differentiate between different vulnerability sources.
# This would reduce data redundancy and make querying more efficient.

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

class CrowdStrikeMalware(models.Model):
    malware_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    ttps = models.JSONField(null=True, blank=True)  # Tactics, Techniques, and Procedures
    targeted_industries = models.JSONField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    activity_start_date = models.DateTimeField(null=True, blank=True)
    activity_end_date = models.DateTimeField(null=True, blank=True)
    threat_groups = models.JSONField(null=True, blank=True)  # Associated threat groups/actors
    last_update_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class CISAKev(models.Model):
    """
    Model for CISA Known Exploited Vulnerabilities.
    """
    cve_id = models.CharField(max_length=50, unique=True)
    vulnerability_name = models.CharField(max_length=500)
    description = models.TextField()
    date_added = models.DateField()
    due_date = models.DateField()
    vendor_project = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CISA Known Exploited Vulnerability"
        verbose_name_plural = "CISA Known Exploited Vulnerabilities"
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['cve_id']),
            models.Index(fields=['date_added']),
            models.Index(fields=['vendor_project']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.cve_id} - {self.vulnerability_name}"

class CrowdStrikeTailoredIntel(models.Model):
    """
    Model for CrowdStrike Tailored Intelligence reports.
    """
    report_id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    publish_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    report_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Keep original fields for backward compatibility
    threat_groups = models.TextField(null=True, blank=True)  # Comma-separated list
    targeted_sectors = models.TextField(null=True, blank=True)  # Comma-separated list
    
    # Add new JSON fields
    threat_groups_json = models.JSONField(default=list, null=True, blank=True)
    targeted_sectors_json = models.JSONField(default=list, null=True, blank=True)
    
    class Meta:
        verbose_name = "CrowdStrike Tailored Intel"
        verbose_name_plural = "CrowdStrike Tailored Intel"
        indexes = [
            models.Index(fields=['publish_date']),
            models.Index(fields=['last_updated']),
            models.Index(fields=['title']),
        ]
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Convert text fields to JSON fields when saving
        if self.threat_groups and not self.threat_groups_json:
            self.threat_groups_json = [group.strip() for group in self.threat_groups.split(',') if group.strip()]
            
        if self.targeted_sectors and not self.targeted_sectors_json:
            self.targeted_sectors_json = [sector.strip() for sector in self.targeted_sectors.split(',') if sector.strip()]
        
        super().save(*args, **kwargs)
