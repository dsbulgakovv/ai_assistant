from .start import setup_start_handlers
from .calendar.start import setup_calendar_start_handlers
from .calendar.create_manual_task import setup_calendar_create_task_handlers
from .calendar.calendar_util import setup_calendar_dialogue_select_date_handlers
from .voice_to_text import setup_voice_to_text_handler
from .q_and_a import setup_q_and_a_handlers
from .uncertainty import setup_uncertainty_handlers


def setup_handlers(dp):
    setup_start_handlers(dp)
    setup_calendar_start_handlers(dp)
    setup_calendar_create_task_handlers(dp)
    setup_voice_to_text_handler(dp)
    setup_q_and_a_handlers(dp)
    setup_uncertainty_handlers(dp)
    # the latest
    setup_calendar_dialogue_select_date_handlers(dp)
