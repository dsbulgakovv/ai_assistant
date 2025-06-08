import sys
import logging
from aiogram import Bot
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


async def schedule_event(
        scheduler: AsyncIOScheduler, event_id: int,
        run_datetime: datetime, bot: Bot, chat_id: int, text: str
):
    """Добавляем задачу с уникальным ID = str(event_id)"""
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=run_datetime,
        args=[bot, chat_id, text],
        id=str(event_id),
        replace_existing=True
    )


async def remove_event(scheduler: AsyncIOScheduler, event_id: int):
    """Отключить напоминание, если событие удалили или изменили"""
    try:
        await scheduler.remove_job(str(event_id))
    except Exception as e:
        logger.debug(e)


async def send_reminder(bot: Bot, chat_id: int, text: str):
    await bot.send_message(chat_id, text)
