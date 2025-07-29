from datetime import date

from django.db import models
from django.db.models import PROTECT
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_crf.model_mixins import SingletonCrfModelMixin
from edc_dx_review.model_mixins import (
    ClinicalReviewBaselineModelMixin,
    ClinicalReviewModelMixin,
    dx_initial_review_model_mixin_factory,
    rx_initial_review_model_mixin_factory,
)
from edc_dx_review.model_mixins.factory import (
    baseline_review_model_mixin_factory,
    followup_review_model_mixin_factory,
)
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.models import SubjectVisit

from dx_app.consents import consent_v1


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


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


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class ClinicalReviewBaseline(
    baseline_review_model_mixin_factory(),
    ClinicalReviewBaselineModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @classmethod
    def related_visit_model_attr(cls):
        return "subject_visit"

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class ClinicalReview(
    followup_review_model_mixin_factory(),
    ClinicalReviewModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class DmInitialReview(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="medicines for diabetes"
    ),
    SingletonCrfModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class HtnInitialReview(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="medicines for hypertension"
    ),
    SingletonCrfModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class HivInitialReview(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="antiretroviral therapy (ART)"
    ),
    SingletonCrfModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class DmInitialReviewMissingSingleton(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="medicines for diabetes"
    ),
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class HtnInitialReviewMissingSingleton(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="medicines for hypertension"
    ),
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier


class HivInitialReviewMissingSingleton(
    dx_initial_review_model_mixin_factory(),
    rx_initial_review_model_mixin_factory(
        "rx_init", verbose_name_label="antiretroviral therapy (ART)"
    ),
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    @property
    def related_visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier
