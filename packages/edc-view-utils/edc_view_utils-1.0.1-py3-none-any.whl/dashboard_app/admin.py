from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_locator.models import SubjectLocator

from .models import Appointment, SubjectConsent, SubjectVisit


class AdminSite(DjangoAdminSite):
    pass


dashboard_app_admin = AdminSite(name="dashboard_app_admin")

dashboard_app_admin.register(Appointment)
dashboard_app_admin.register(SubjectConsent)
dashboard_app_admin.register(SubjectLocator)
dashboard_app_admin.register(SubjectVisit)
