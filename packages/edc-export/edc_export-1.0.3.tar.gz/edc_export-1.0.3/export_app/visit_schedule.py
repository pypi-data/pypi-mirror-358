from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule

from .consents import consent_v1


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="edc_appointment.subjectrequisition", name=name)


panel_one = MockPanel(name="one")
panel_two = MockPanel(name="two")
panel_three = MockPanel(name="three")
panel_four = MockPanel(name="four")
panel_five = MockPanel(name="five")
panel_six = MockPanel(name="six")

crfs = CrfCollection(
    Crf(show_order=1, model="export_app.crfone", required=True),
    Crf(show_order=2, model="export_app.crftwo", required=True),
    Crf(show_order=3, model="export_app.crfthree", required=True),
    Crf(show_order=4, model="export_app.crffour", required=True),
    Crf(show_order=5, model="export_app.crffive", required=True),
)

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=panel_one, required=True, additional=False),
    Requisition(show_order=20, panel=panel_two, required=True, additional=False),
    Requisition(show_order=30, panel=panel_three, required=True, additional=False),
    Requisition(show_order=40, panel=panel_four, required=True, additional=False),
    Requisition(show_order=50, panel=panel_five, required=True, additional=False),
    Requisition(show_order=60, panel=panel_six, required=True, additional=False),
)


crfs_unscheduled = CrfCollection(
    Crf(show_order=1, model="export_app.crfone", required=True),
    Crf(show_order=3, model="export_app.crfthree", required=True),
    Crf(show_order=5, model="export_app.crffive", required=True),
)


visit_schedule1 = VisitSchedule(
    name="visit_schedule1",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_adverse_event.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule1 = Schedule(
    name="schedule1",
    onschedule_model="export_app.onscheduleone",
    offschedule_model="export_app.offscheduleone",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent_v1],
)


visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
            requisitions_unscheduled=requisitions,
            crfs_unscheduled=crfs_unscheduled,
            allow_unscheduled=True,
            facility_name="5-day-clinic",
        )
    )
for visit in visits:
    schedule1.add_visit(visit)

visits = []
for index in range(4, 8):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
            facility_name="7-day-clinic",
        )
    )
visit_schedule1.add_schedule(schedule1)
