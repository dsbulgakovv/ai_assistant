import sys
import logging
from core import bot
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


def schedule_event(
        scheduler: AsyncIOScheduler, event_id: int,
        run_datetime: datetime, chat_id: int, text: str
):
    """Добавляем задачу с уникальным ID = str(event_id)"""
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=run_datetime,
        args=[chat_id, text],
        id=str(event_id),
        replace_existing=True
    )


def remove_event(scheduler: AsyncIOScheduler, event_id: int):
    """Отключить напоминание, если событие удалили или изменили"""
    try:
        scheduler.remove_job(str(event_id))
    except Exception as e:
        logger.debug(e)


async def send_reminder(chat_id: int, text: str):
    await bot.send_message(chat_id, text)
