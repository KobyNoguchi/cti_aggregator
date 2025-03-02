from django.contrib import admin
from .models import (
    IntelligenceArticle, Vulnerability, CrowdStrikeIntel,
    CrowdStrikeMalware, CISAKev
)

# Register your models here.

@admin.register(CISAKev)
class CISAKevAdmin(admin.ModelAdmin):
    list_display = ['cve_id', 'vulnerability_name', 'date_added', 'due_date']
    list_filter = ['date_added', 'due_date']
    search_fields = ['cve_id', 'vulnerability_name', 'description', 'vendor_project', 'product']
    readonly_fields = ['created_at', 'updated_at']
