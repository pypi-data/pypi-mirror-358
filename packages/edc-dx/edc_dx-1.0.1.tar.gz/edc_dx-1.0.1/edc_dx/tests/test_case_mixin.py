from django.apps import apps as django_apps
from django.test import TestCase
from edc_action_item import site_action_items
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_reportable.data.grading_data.daids_july_2017 import grading_data
from edc_reportable.data.normal_data.africa import normal_data
from edc_reportable.utils import load_reference_ranges
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from dx_app.models import SubjectConsent
from dx_app.visit_schedule import visit_schedule


class TestCaseMixin(TestCase):
    @classmethod
    def setUpClass(cls):
        site_action_items.registry = {}
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        load_reference_ranges(
            "my_reportables", normal_data=normal_data, grading_data=grading_data
        )
        site_visit_schedules.register(visit_schedule)

    @staticmethod
    def enroll(subject_identifier=None):
        subject_identifier = subject_identifier or "1111111"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier, consent_datetime=get_utcnow()
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model("dx_app.onschedule")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_identifier

    @staticmethod
    def fake_enroll():
        subject_identifier = "2222222"
        RegisteredSubject.objects.create(subject_identifier=subject_identifier)
        return subject_identifier

    def create_visits(self, subject_identifier):
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code="1000",
            visit_code_sequence=0,
        )
        self.subject_visit_baseline = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
            visit_code="1000",
            visit_code_sequence=0,
        )

        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code="1010",
            visit_code_sequence=0,
        )
        self.subject_visit_followup = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
            visit_code="1010",
            visit_code_sequence=0,
        )
