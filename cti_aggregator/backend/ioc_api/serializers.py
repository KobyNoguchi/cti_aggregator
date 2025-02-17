from rest_framework import serializers
from ioc_scraper.models import Vulnerability

class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = '__all__'
