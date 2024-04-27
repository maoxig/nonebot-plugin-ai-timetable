from datetime import datetime
from .model import User
import re

from typing import Union
from nonebot.matcher import Matcher
from nonebot import on_command, on_regex, require, logger, get_plugin_config
from nonebot.adapters import Message, Event, Bot
from .config import Config


require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page, md_to_pic
from nonebot_plugin_alconna import UniMessage

try:
    from nonebot_plugin_apscheduler import scheduler
except ImportError:
    logger.opt(colors=True).info(
        "未检测到软依赖<y>nonebot_plugin_apscheduler</y>,<r>禁用定时任务功能</r>"
    )
    scheduler = None

__base_url_pattern__ = r"https://cdn\.cnbj1\.fds\.api\.mi-img.com/miai-fe-aischedule-wx-redirect-fe/redirect.html\?linkToken=.+"

__response_url_pattern = r"^(https://i\.ai\.mi\.com/course-multi/table\?)*(ctId=)\d+(&userId=)\d*[1-9]\d*(&deviceId=)[0-9a-zA-Z]*(&sourceName=course-app-browser)"
config = get_plugin_config(Config)


async def check_user(event: Event, matcher: Matcher):
    if not User.check_user_in_table(event.get_user_id()):
        await matcher.finish("你还没有导入课表，发送/导入课表来导入吧！")


async def check_scheduler(event: Event, matcher: Matcher):
    if not scheduler:
        await matcher.finish("没有apscheduler，无法使用定时任务功能")


async def check_base_url(key: str):
    text = key
    if re.match(__base_url_pattern__, text):
        return key


def weekday_int(key) -> int:
    """中文日期转数字"""
    cn2an = {
        "今": datetime.now().weekday() + 1,
        "明": datetime.now().weekday() + 2,
        "昨": datetime.now().weekday(),
        "后": datetime.now().weekday() + 3,
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "日": 7,
        "天": 7,
    }
    for i in cn2an:
        if i in key:
            return cn2an[i]
    return 7


async def new_table():
    pass


async def update_table(uid: str, url: str):
    pass


async def build_table():
    pass


async def build_table_for_morning():
    pass


async def build_table_for_day():
    pass


async def build_table_for_current_week():
    pass


async def build_table_for_next_week():
    pass


async def build_table_for_current_course():
    pass


async def build_table_for_next_course():
    pass


async def send_table(matcher: Matcher, table: Union[str, bytes]):
    """课表发送函数，根据不同设置，决定发送什么类型的消息"""
    if isinstance(table, str):
        if config.timetable_pic:
            pic = await md_to_pic(table)
            return await UniMessage.image(raw=pic).send()
        else:
            return await matcher.send(table)
    else:
        return await UniMessage.image(raw=table).send()
