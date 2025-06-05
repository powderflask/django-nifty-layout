from django.shortcuts import render
from .models import SiteInspectionReport
from .layouts import layout


def report_view(request):
    try:
        report = SiteInspectionReport.objects.all()[0]
    except IndexError:
        return render(request, "reports/404.html")
    return render(request, "reports/report.html", context={"bound_node": layout.bind(report)})
