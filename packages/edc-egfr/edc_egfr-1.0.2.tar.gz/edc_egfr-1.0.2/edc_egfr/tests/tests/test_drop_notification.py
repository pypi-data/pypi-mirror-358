from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_appointment.constants import SCHEDULED_APPT
from edc_appointment.models import Appointment
from edc_constants.constants import BLACK, CLOSED, COMPLETE, INCOMPLETE, MALE, OPEN
from edc_lab import site_labs
from edc_lab.models import Panel
from edc_lab_panel.panels import rft_panel
from edc_registration.models import RegisteredSubject
from edc_reportable import MICROMOLES_PER_LITER
from edc_reportable.data.grading_data.daids_july_2017 import grading_data
from edc_reportable.data.normal_data.africa import normal_data
from edc_reportable.utils import load_reference_ranges
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_egfr.egfr import Egfr
from egfr_app.lab_profiles import lab_profile
from egfr_app.models import (
    EgfrDropNotification,
    ResultCrf,
    SubjectRequisition,
    SubjectVisit,
)
from egfr_app.visit_schedules import visit_schedule


class TestEgfr(TestCase):
    def setUp(self) -> None:
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        RegisteredSubject.objects.create(
            subject_identifier="1234",
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=30),
            ethnicity=BLACK,
        )
        appointment = Appointment.objects.create(
            subject_identifier="1234",
            appt_datetime=get_utcnow(),
            timepoint=0,
            visit_code=DAY1,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            appt_reason=SCHEDULED_APPT,
        )
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier="1234",
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            visit_code=DAY1,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            reason=SCHEDULED,
        )

        panel = Panel.objects.get(name=rft_panel.name)

        requisition = SubjectRequisition.objects.create(
            subject_identifier="1234",
            subject_visit=self.subject_visit,
            report_datetime=appointment.appt_datetime,
            panel=panel,
        )
        self.crf = ResultCrf.objects.create(
            subject_visit=self.subject_visit,
            requisition=requisition,
            report_datetime=appointment.appt_datetime,
            assay_datetime=appointment.appt_datetime,
            egfr_value=156.43,
            creatinine_value=53,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.opts = dict(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

    @classmethod
    def setUpTestData(cls):
        load_reference_ranges(
            "my_reference_list", normal_data=normal_data, grading_data=grading_data
        )
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)

    @override_settings(EDC_EGFR_DROP_NOTIFICATION_MODEL="egfr_app.EgfrDropNotification")
    def test_egfr_drop_notification_model(self):
        Egfr(
            baseline_egfr_value=220.1,
            percent_drop_threshold=20,
            calling_crf=self.crf,
            **self.opts,
        )
        obj = EgfrDropNotification.objects.get(subject_visit=self.subject_visit)
        obj.report_status = OPEN
        obj.save()
        self.assertEqual(obj.crf_status, INCOMPLETE)
        obj.report_status = CLOSED
        obj.save()
        self.assertEqual(obj.crf_status, COMPLETE)
