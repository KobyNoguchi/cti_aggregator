# Generated by Django 5.1.6 on 2025-03-12 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ioc_scraper', '0011_cisakev_ioc_scraper_cve_id_40d6de_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='intelligencearticle',
            name='target_industries',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='intelligencearticle',
            name='threat_actor_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
