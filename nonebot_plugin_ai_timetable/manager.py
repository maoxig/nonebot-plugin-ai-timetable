from datetime import datetime
from .model import *
import re
import time
import httpx
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


__headers__ = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63"
}
__day_pattern__ = r"((星期|周)([一二三四五六日1-7]))|((今|明|昨|后)(天|日))"


async def check_user(event: Event, matcher: Matcher) -> Event:
    if not await check_user_in_table(event.get_user_id()):
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


__response_url__ = None


async def response_listener(response):
    """监听请求"""
    global __response_url__
    if re.match(__response_url_pattern, response.url):

        __response_url__ = response.url


async def get_user_data(base_url: str) -> dict:
    async with get_new_page(viewport={"width": 1000, "height": 1200}) as page:

        page.on(
            "response",
            response_listener,
        )
        await page.goto(url=base_url, wait_until="networkidle")
        if __response_url__:
            async with httpx.AsyncClient() as client:
                res = await client.get(__response_url__, headers=__headers__)
            return res.json()["data"]


async def update_table(uid: str, url: str):
    """导入课表，存在|不存在该用户"""
    user_data = await get_user_data(url)
    if await check_user_in_table(uid):
        await update_user(uid, url, __response_url__, user_data)
    else:
        await add_user(uid, url, __response_url__, user_data)


async def build_table(uid: str, key: str):
    key = key.strip()
    if re.match(__day_pattern__, key):
        day = weekday_int(
            key
        )  ##day是1-7的整数，但是也有可能是负数和大于7的数，用于判断周数
        return await build_table_for_day(uid, day)
    elif key == "本周":
        return await build_table_for_current_week(uid)
    elif key == "下周":
        return await build_table_for_next_week(uid)
    elif key == "早八":
        return await build_table_for_morning(uid)
    elif key == "下节课":
        return await build_table_for_next_course(uid)
    else:
        return "参数匹配失败"


async def build_table_for_morning(uid: str):
    pass


async def build_table_for_day(uid: str, day: int):
    """构造某日课表信息"""
    courses = await query_course_by_day(uid, day)
    week = await get_current_week(uid, day)
    user = await query_user_by_uid(uid)
    if day < 0:
        day += 7
        week -= 1
    elif day > 7:
        day -= 7
        week += 1
    courses = [course for course in courses if str(week) in course.weeks.split(",")]
    msg = "|时间|课程|地点|\n| :-----| :----: | :----: |"
    for course in courses:
        sections = course.sections.split(",")
        startsection = int(sections[0])
        endsection = int(sections[-1])
        starttime = eval(user.sectionTimes)[startsection - 1]["s"]
        endtime = eval(user.sectionTimes)[endsection - 1]["e"]
        msg = (msg+ "\n"+ "|"+ starttime+ "-"+ endtime+ "|"+ course.name+ "|"+ course.position)
    return msg


async def build_table_for_current_week(uid: str) -> bytes:
    """获取本周课表，以后考虑通过本地生成"""
    user_data = await query_user_by_uid(uid)
    async with get_new_page(viewport={"width": 1000, "height": 1000}) as page:
        await page.goto(user_data.base_url, wait_until="networkidle")
        await page.evaluate(
            'var t = document.querySelector("#root>div>div.importSchedule___UjEKt>div.footer___1iAis.toUp___2mciB"); t.style.display = "none"'
        )
        pic = await page.screenshot(full_page=True, type="jpeg", quality=70)
        return pic


async def build_table_for_next_week(uid: str) -> bytes:
    """获取本周课表，以后考虑通过本地生成"""
    user_data = await query_user_by_uid(uid)
    async with get_new_page(viewport={"width": 1000, "height": 1000}) as page:
        await page.goto(user_data.base_url, wait_until="networkidle")
        await page.evaluate(
            'var t = document.querySelector("#root>div>div.importSchedule___UjEKt>div.footer___1iAis.toUp___2mciB"); t.style.display = "none"'
        )
        await page.click(
            "#schedule-view > div.header___26sI1 > div.presentWeek___-o65e > div.rightBtn___2ZhSY"
        )
        pic = await page.screenshot(full_page=True, type="jpeg", quality=70)
        return pic


async def build_table_for_next_course(uid: str):
    pass


async def build_table_for_some_course(uid: str, key: str):
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
