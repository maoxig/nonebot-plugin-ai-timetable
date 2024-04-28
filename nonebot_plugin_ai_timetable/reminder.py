from nonebot.adapters import Message, Event, Bot
from nonebot.matcher import Matcher
from nonebot import logger,require
require("nonebot_plugin_orm")
require("nonebot_plugin_apscheduler")
try:
    from nonebot_plugin_apscheduler import scheduler
except ImportError:
    logger.opt(colors=True).info(
        "未检测到软依赖<y>nonebot_plugin_apscheduler</y>,<r>禁用定时任务功能</r>"
    )
    scheduler = None



async def add_reminders(uid: str, text: str, bot: Bot, event: Event, matcher: Matcher):
    pass


async def add_reminder_for_day():
    pass


async def add_reminder_for_morning():
    pass


async def add_reminder_for_course():
    pass


async def remove_reminder_for_day():
    pass


async def remove_reminder_for_morning():
    pass


async def remove_reminder_for_course():
    pass
