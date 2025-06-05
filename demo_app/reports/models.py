from django.db import models
from django.utils import timezone


class SiteInspectionReport(models.Model):
    # Metadata
    report_id = models.CharField(max_length=64, unique=True, verbose_name='Report ID')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    # Site details
    site_name = models.CharField(max_length=255, verbose_name='Site Name')
    site_address = models.TextField(verbose_name='Site Address')
    site_contact_person = models.CharField(max_length=255, verbose_name='Site Contact Person')
    site_contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Site Contact Phone')
    site_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Latitude')
    site_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Longitude')

    # Inspector details
    inspector_name = models.CharField(max_length=255, verbose_name='Inspector Name')
    inspector_id = models.CharField(max_length=64, verbose_name='Inspector ID')
    inspector_department = models.CharField(max_length=128, verbose_name='Inspector Department')

    # Inspection metadata
    inspection_date = models.DateField(verbose_name='Inspection Date')
    inspection_duration_minutes = models.PositiveIntegerField(verbose_name='Inspection Duration (minutes)')
    inspection_type = models.CharField(
        max_length=64,
        choices=[('routine', 'Routine'), ('follow_up', 'Follow-Up'), ('emergency', 'Emergency')],
        verbose_name='Inspection Type'
    )

    # Key findings
    finding_summary = models.TextField(verbose_name='Finding Summary')
    finding_safety_issues = models.TextField(blank=True, verbose_name='Safety Issues')
    finding_compliance_issues = models.TextField(blank=True, verbose_name='Compliance Issues')
    finding_structural_issues = models.TextField(blank=True, verbose_name='Structural Issues')
    finding_environmental_issues = models.TextField(blank=True, verbose_name='Environmental Issues')

    # Ratings
    rating_safety = models.PositiveSmallIntegerField(default=0, verbose_name='Safety Rating')
    rating_compliance = models.PositiveSmallIntegerField(default=0, verbose_name='Compliance Rating')
    rating_cleanliness = models.PositiveSmallIntegerField(default=0, verbose_name='Cleanliness Rating')
    rating_overall = models.PositiveSmallIntegerField(default=0, verbose_name='Overall Rating')

    # Recommendations
    recommendation_immediate_action = models.TextField(blank=True, verbose_name='Immediate Action Required')
    recommendation_long_term_action = models.TextField(blank=True, verbose_name='Long Term Action Required')
    recommendation_notes = models.TextField(blank=True, verbose_name='Additional Notes')

    def __str__(self):
        return f"Inspection Report: {self.report_id} ({self.site_name})"
