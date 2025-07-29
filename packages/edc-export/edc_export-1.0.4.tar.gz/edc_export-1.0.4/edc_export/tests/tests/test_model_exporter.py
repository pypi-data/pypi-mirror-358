import csv
from tempfile import mkdtemp

from django.test import TestCase, override_settings
from edc_facility.import_holidays import import_holidays
from edc_pdutils.df_exporters import CsvModelExporter
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from export_app.models import Crf, CrfEncrypted, SubjectVisit
from export_app.visit_schedule import visit_schedule1

from ...utils import get_export_folder
from ..create_crfs import create_crfs
from ..helper import Helper


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp())
class TestExport(TestCase):
    helper_cls = Helper

    def setUp(self):
        import_holidays()
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule1)
        for i in range(0, 7):
            helper = self.helper_cls(subject_identifier=f"subject-{i}")
            helper.consent_and_put_on_schedule(
                visit_schedule_name=visit_schedule1.name,
                schedule_name="schedule1",
                report_datetime=get_utcnow(),
            )
        create_crfs(5)
        self.subject_visit = SubjectVisit.objects.all()[0]

    def test_encrypted_to_csv_from_qs(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model_exporter = CsvModelExporter(
            queryset=CrfEncrypted.objects.all(),
            export_folder=get_export_folder(),
        )
        model_exporter.to_csv()

    def test_encrypted_to_csv_from_model(self):
        CrfEncrypted.objects.create(subject_visit=self.subject_visit, encrypted1="encrypted1")
        model_exporter = CsvModelExporter(
            model="export_app.CrfEncrypted",
            export_folder=get_export_folder(),
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_qs(self):
        model_exporter = CsvModelExporter(
            queryset=Crf.objects.all(), export_folder=get_export_folder()
        )
        model_exporter.to_csv()

    def test_records_to_csv_from_model(self):
        model_exporter = CsvModelExporter(
            model="export_app.crf",
            sort_by=["subject_identifier", "visit_code"],
            export_folder=get_export_folder(),
        )
        exported = model_exporter.to_csv()
        with open(exported.path, "r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            rows = [row for row in enumerate(csv_reader)]
        self.assertEqual(len(rows), 4)
        for i, crf in enumerate(
            Crf.objects.all().order_by(
                "subject_visit__subject_identifier", "subject_visit__visit_code"
            )
        ):
            self.assertEqual(
                rows[i][1].get("subject_identifier"), crf.subject_visit.subject_identifier
            )
            self.assertEqual(rows[i][1].get("visit_code"), crf.subject_visit.visit_code)
