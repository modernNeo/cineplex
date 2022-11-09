from django.urls import path

from cineplex.views import Index, AuditLogs

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('audit_logs', AuditLogs.as_view(), name="audit_logs"),
]