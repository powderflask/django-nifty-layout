from django.core.management.base import BaseCommand
from django.utils import timezone

from reports.models import SiteInspectionReport


# from reports.models import SiteInspectionReport


class Command(BaseCommand):
    help = "Seeds the database with an example SiteInspectionReport."

    def handle(self, *args, **options):
        example_data = {
            "report_id": "RPT-2025-00123",
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "site_name": "Acme Manufacturing Plant #12",
            "site_address": "456 Industrial Park Drive\nSpringfield, IL 62704",
            "site_contact_person": "Maria Gonzales",
            "site_contact_phone": "+1-217-555-0147",
            "site_latitude": 39.7817,
            "site_longitude": -89.6501,
            "inspector_name": "James Holloway",
            "inspector_id": "INS-0458",
            "inspector_department": "Health & Safety Compliance",
            "inspection_date": timezone.now().date(),
            "inspection_duration_minutes": 135,
            "inspection_type": "routine",
            "finding_summary": (
                "Inspection identified several moderate safety and compliance issues. "
                "No major structural faults were noted, but safety signage was lacking in key areas."
            ),
            "finding_safety_issues": (
                "- Inadequate placement of fire extinguishers\n"
                "- Missing safety signage in chemical storage room"
            ),
            "finding_compliance_issues": (
                "- Improper labeling of hazardous materials\n"
                "- Expired MSDS documentation in break room"
            ),
            "finding_structural_issues": "",
            "finding_environmental_issues": "Minor leakage near waste processing unit.",
            "rating_safety": 3,
            "rating_compliance": 2,
            "rating_cleanliness": 4,
            "rating_overall": 3,
            "recommendation_immediate_action": (
                "Replace expired MSDS sheets and update hazard labels by next week."
            ),
            "recommendation_long_term_action": (
                "Implement a digital compliance tracking system and schedule monthly checks."
            ),
            "recommendation_notes": "Follow-up inspection recommended in 90 days.",
        }

        report, created = SiteInspectionReport.objects.get_or_create(
            report_id=example_data["report_id"],
            defaults=example_data
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created demo report"))
        else:
            self.stdout.write(self.style.WARNING(f"Demo report already exists"))
