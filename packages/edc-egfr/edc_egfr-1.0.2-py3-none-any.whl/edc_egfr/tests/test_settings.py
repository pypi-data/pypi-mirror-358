#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_egfr"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
    ],
    ETC_DIR=base_dir / app_name / "tests" / "etc",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    EDC_SITES_REGISTER_DEFAULT=True,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_results.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_reportable.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "edc_egfr.apps.AppConfig",
        "egfr_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
