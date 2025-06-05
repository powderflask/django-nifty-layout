from django.utils.html import escape
from django.utils.safestring import SafeString

from nifty_layout.components import DictCompositeNode as Dct, Seq, FieldNode

layout = Dct(dict(
    metadata=Seq(
        "report_id",
        "created_at",
        "updated_at",
    ),
    site_details=Seq(
        "site_name",
        FieldNode("site_address", formatter=lambda x: SafeString(f"<u>%s</u>" % escape(x))),
        "site_contact_person",
        "site_contact_phone",
        "site_latitude",
        "site_longitude",
    ),
    inspector_details=Seq(
        "inspector_name",
        "inspector_id",
        "inspector_department",
    ),
    inspection_info=Seq(
        "inspection_date",
        "inspection_duration_minutes",
        "inspection_type",
    ),
    findings=Dct(dict(
        summary="finding_summary",
        all=Seq(
            "finding_safety_issues",
            "finding_compliance_issues",
            "finding_environmental_issues",
        ),
    )),
    ratings=Dct(dict(
        overall=FieldNode("rating_overall", labeller="Overall"),
        all=Seq(
            FieldNode("rating_safety", labeller="Safety"),
            FieldNode("rating_compliance", labeller="Compliance"),
            FieldNode("rating_cleanliness", labeller="Cleanliness"),
        ),
    )),
    recommendations=Seq(
        "recommendation_immediate_action",
    )
))

