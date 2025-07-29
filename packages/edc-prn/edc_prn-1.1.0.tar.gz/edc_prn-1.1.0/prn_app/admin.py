from django.contrib import admin

from edc_prn.modeladmin_mixins import PrnModelAdminMixin

from .models import TestModel


@admin.register(TestModel)
class TestModelAdmin(PrnModelAdminMixin, admin.ModelAdmin):
    pass
