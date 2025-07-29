from datetime import date

from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields import EncryptedCharField
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_constants.constants import YES
from edc_crf.model_mixins import CrfWithActionModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_lab.model_mixins import RequisitionModelMixin
from edc_list_data.model_mixins import BaseListModelMixin, ListModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins.off_schedule_model_mixin import (
    OffScheduleModelMixin,
)
from edc_visit_schedule.model_mixins.on_schedule_model_mixin import OnScheduleModelMixin
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)

from edc_export.managers import ExportHistoryManager
from edc_export.model_mixins import ExportTrackingFieldsModelMixin


class SubjectScreening(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    screening_identifier = models.CharField(max_length=50)

    screening_datetime = models.DateTimeField(default=get_utcnow)

    age_in_years = models.IntegerField(default=25)


class SubjectConsent(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))

    citizen = models.CharField(max_length=25, default=YES)

    legal_marriage = models.CharField(max_length=25, null=True)

    marriage_certificate = models.CharField(max_length=25, null=True)


class SubjectConsentV1(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectVisit(SiteModelMixin, VisitModelMixin, BaseUuidModel):
    survival_status = models.CharField(max_length=25, null=True)

    last_alive_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ["report_datetime"]


class SubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Missed Visit Reasons"
        verbose_name_plural = "Subject Missed Visit Reasons"


class SubjectVisitMissed(
    SubjectVisitMissedModelMixin,
    CrfWithActionModelMixin,
    BaseUuidModel,
):
    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(
        SubjectVisitMissedModelMixin.Meta,
        BaseUuidModel.Meta,
    ):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"


class SubjectLocator(BaseUuidModel):
    subject_identifier = models.CharField(max_length=36)


class CrfModelMixin(SiteModelMixin, models.Model):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(null=True)

    @property
    def visit_code(self):
        return self.subject_visit.visit_code

    @property
    def related_visit(self):
        return self.subject_visit

    class Meta:
        abstract = True


class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):
    panel_name = models.CharField(max_length=25, default="Microtube")


class ListModel(ListModelMixin):
    pass


class Crf(CrfModelMixin, ExportTrackingFieldsModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    char1 = models.CharField(max_length=25, null=True)

    date1 = models.DateTimeField(null=True)

    int1 = models.IntegerField(null=True)

    uuid1 = models.UUIDField(null=True)

    m2m = models.ManyToManyField(ListModel)

    export_history = ExportHistoryManager()


class CrfEncrypted(CrfModelMixin, ExportTrackingFieldsModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    encrypted1 = EncryptedCharField(null=True)

    export_history = ExportHistoryManager()


class CrfOne(CrfModelMixin, BaseUuidModel):
    dte = models.DateTimeField(default=get_utcnow)


class CrfTwo(CrfModelMixin, BaseUuidModel):
    dte = models.DateTimeField(default=get_utcnow)


class CrfThree(CrfModelMixin, BaseUuidModel):
    UPPERCASE = models.DateTimeField(default=get_utcnow)


class ListOne(BaseListModelMixin, BaseUuidModel):
    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class ListTwo(BaseListModelMixin, BaseUuidModel):
    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class CrfWithInline(CrfModelMixin, BaseUuidModel):
    list_one = models.ForeignKey(ListOne, on_delete=models.PROTECT)

    list_two = models.ForeignKey(ListTwo, on_delete=models.PROTECT)

    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class OnScheduleOne(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class SubjectOffstudy(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()
