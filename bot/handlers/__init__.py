from .start import setup_start_handlers
from .calendar import setup_calendar_handlers
from .voice_to_text import setup_voice_to_text_handler
from .q_and_a import setup_q_and_a_handlers


def setup_handlers(dp):
    setup_start_handlers(dp)
    setup_calendar_handlers(dp)
    setup_voice_to_text_handler(dp)
    setup_q_and_a_handlers(dp)
