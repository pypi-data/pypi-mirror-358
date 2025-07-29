from datetime import date

from django.db import models
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins import ConsentVersionModelMixin
from edc_crf.model_mixins import CrfModelMixin, CrfStatusModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.models import SubjectVisit

from prn_app.consents import consent_v1


class TestModel(models.Model):
    f1 = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name = "Test Model"


class SubjectConsent(
    SiteModelMixin,
    ConsentVersionModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25)

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


class Crf(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        pass


class Prn(SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(BaseUuidModel.Meta):
        pass


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass
