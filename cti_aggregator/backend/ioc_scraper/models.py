from django.db import models

class Vulnerability(models.Model):
    cve_id = models.CharField(max_length=50, unique=True, null=False,default="Unknown_CVE")
    vulnerability_name = models.CharField(max_length=500)
    description = models.TextField()
    severity = models.CharField(max_length=50)
    published_date = models.DateField()
    source_url = models.URLField()

    def __str__(self):
        return f"{self.cve_id} - {self.vulnerability_name}"
