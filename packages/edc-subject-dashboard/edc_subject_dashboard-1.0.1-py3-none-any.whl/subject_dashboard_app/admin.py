from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_locator.models import SubjectLocator

from .models import Appointment, SubjectConsent, SubjectVisit


class AdminSite(DjangoAdminSite):
    pass


subject_dashboard_app_admin = AdminSite(name="subject_dashboard_app_admin")

subject_dashboard_app_admin.register(Appointment)
subject_dashboard_app_admin.register(SubjectConsent)
subject_dashboard_app_admin.register(SubjectLocator)
subject_dashboard_app_admin.register(SubjectVisit)
