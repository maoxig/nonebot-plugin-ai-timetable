from nonebot.adapters import  Event, Bot
from nonebot.matcher import Matcher
from nonebot import logger, require
from typing import List
import re
import random

require("nonebot_plugin_orm")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import UniMessage
from nonebot.exception import ActionFailed
from nonebot_plugin_apscheduler import scheduler
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime,timedelta
from .data_manager import query_user_by_uid, weekday_int,query_course_by_name
from .manager import (
    get_courses_by_day,
    build_table_by_courses_list,
    config,
    md_to_pic
)

__day_pattern__ = r"(星期|周)([一二三四五六日1-7])"


"""
job_id的格式按照 str[uid,type]进行区分
例如
'11415,周1'
'11415,数分1'
'11415,早八1'

"""


async def check_scheduler(event: Event, matcher: Matcher):
    """检查apscheduler依赖是否存在"""
    if not scheduler:
        await matcher.finish("没有apscheduler，无法使用定时任务功能")


async def add_reminders(uid: str, key: str, bot: Bot, event: Event):
    """添加提醒处理分发函数"""
    if re.match(__day_pattern__, key):
        day = weekday_int(
            key
        )  ##day是1-7的整数，但是也有可能是负数和大于7的数，用于判断周数
        job_list = await add_reminder_for_day(uid, day, bot, event)
    elif key == "早八":
        job_list=await add_reminder_for_morning(uid,bot,event)
    else:
        job_list=await add_reminder_for_course(uid,key,bot,event)
    
    return f"成功添加了{len(job_list)}个提醒"


async def remove_reminders(uid: str, key: str):
    """移除提醒处理函数"""
    key = key.strip()
    if re.match(__day_pattern__, key):
        day = weekday_int(
            key
        )  
        job_id = f"{uid},周{day}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id=job_id)
            return "成功移除了你的1个提醒"

    elif key == "早八":
        count=0
        for i,job in enumerate(scheduler.get_jobs()):
            job_name = job.id.split(",")
            if job_name and len(job_name) == 2 and uid==job_name[0] and "早八" in job.id.split(",")[1]:
                count += 1
                scheduler.remove_job(job_id=job.id)
        return f"成功移除了你的{count}个提醒"
    elif key == "全部":
        count = 0
        for i, job in enumerate(scheduler.get_jobs()):
            job_name = job.id.split(",")
            if (
                job_name
                and len(job_name) == 2
                and uid == job_name[0]
            ):
                count += 1
                scheduler.remove_job(job_id=job.id)
        return f"成功移除了你的全部{count}提醒"
    else:
        count=0
        for i, job in enumerate(scheduler.get_jobs()):
            job_name=job.id.split(",")
            if (
                job_name
                and len(job_name) == 2
                and uid == job_name[0]
                and key in job_name[1]
            ):
                count+=1
                scheduler.remove_job(job_id=job.id)
        return f"成功移除了你的{count}个提醒"

    return f"没有找到名为{key}的提醒"


async def add_reminder_for_day(uid: str, day: int, bot: Bot, event: Event) -> List[Job]:
    """添加一周内，某一天的课程提醒，发送时间是前一天的设置时间"""
    job_list = []
    courses = await get_courses_by_day(uid, day)
    user = await query_user_by_uid(uid)
    course_msg = await build_table_by_courses_list(courses, user)
    job_day=day-1#0-6
    job_id = f"{uid},周{day}"
    send_day = (job_day-1) % 7
    cron = CronTrigger(
        hour=config.timetable_alock_someday,
        minute=0,
        second=random.randint(0, 59),
        day_of_week=send_day,
    )
    kwargs = {"bot": bot, "event": event, "course_msg": course_msg}
    job = scheduler.add_job(
        func=send_reminder,
        trigger=cron,
        id=job_id,
        kwargs=kwargs,
        replace_existing=True,
    )
    job_list.append(job)
    return job_list


async def add_reminder_for_morning(uid: str, bot: Bot, event: Event) -> List[Job]:
    """添加所有早八提醒"""
    job_list = []
    user = await query_user_by_uid(uid)
    for sending_day in range(7):
        day=sending_day+2#sending_day=0，apscheduler星期一；day=2，课表星期二
        courses = await get_courses_by_day(uid, day)
        courses = [
            course
            for course in courses
            if "1" in course.sections.split(",")
        ]  # 从当天的课中选出1
        if courses:
            course_msg = await build_table_by_courses_list(courses, user)
        else:
            course_msg = "你明天没有早八，好好休息吧"
        job_id = f"{uid},早八{sending_day}"
        kwargs = {"bot": bot, "event": event, "course_msg": course_msg}
        cron = CronTrigger(
            hour=config.timetable_alock_8,
            minute=0,
            second=random.randint(0, 59),
            day_of_week=sending_day,
        )
        # logger.debug(job_id+course_msg)
        job = scheduler.add_job(
            func=send_reminder,
            trigger=cron,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True,
        )
        job_list.append(job)
    return job_list


async def add_reminder_for_course(
    uid: str, name: str, bot: Bot, event: Event
) -> List[Job]:
    """为课程添加提醒"""
    job_list = []
    user = await query_user_by_uid(uid)
    courses =await query_course_by_name(uid,name)
    if not courses:
        return []
    for i,course in enumerate(courses):
        class_section = int(course.sections.split(",")[0])
        start_time = eval(user.sectionTimes)[class_section - 1][
            "s"
        ]  # 获取课程开始时间
        hours = int(config.timetable_send_time)
        minutes = int((config.timetable_send_time - hours) * 60)  # 从设置中获取提前的分钟数
        time_obj = datetime.strptime(start_time, "%H:%M")  # 将字符串转换为datetim
        new_time_obj = time_obj - timedelta(hours=hours, minutes=minutes)  # 进行时间的运算
        sending_hour = new_time_obj.hour  # 获取发送时间的小时
        sending_minute = new_time_obj.minute  # 获取发送时间的分钟
        sending_day = course.day - 1
        job_id = f"{uid},{course.name}{i}"
        course_msg=await build_table_by_courses_list([course],user)
        kwargs = {"bot": bot, "event": event, "course_msg": course_msg}
        cron = CronTrigger(
            hour=sending_hour,
            minute=sending_minute,
            second=random.randint(0, 59),
            day_of_week=sending_day,
        )
        job = scheduler.add_job(
            func=send_reminder,
            trigger=cron,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True,
        )
        job_list.append(job)

    return job_list

async def query_reminders_by_uid(uid: str) -> str:
    """根据uid查询jobs中符合条件的job，查询依据是job.id"""
    job_list: List[Job] = scheduler.get_jobs()
    job_list = [
        job
        for job in job_list
        if job.id.split(",")
        and len(job.id.split(",")) == 2
        and uid == job.id.split(",")[0]
    ]
    msg = "|UID|类型|发送时间|\n| :----:| :----:| :----: | \n"
    for job in job_list:
        job_type = job.id.split(",")[1]
        # logger.debug(str(job.kwargs))
        cron: CronTrigger = job.trigger
        values=cron.fields
        msg += f"|{uid}|{job_type}|周{int(str(values[4]))+1}-{values[5]}:{values[6]}|\n"
    return msg


async def send_reminder(bot: Bot, event: Event, course_msg: str):
    """提醒发送函数"""
    msg = f"- 现在时间是{ datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, 以下是你预定的课程信息：\n\n"
    msg += course_msg
    try:
        if config.timetable_pic:
            pic =await md_to_pic(msg)
            await UniMessage.image(raw=pic).send(target=event, bot=bot, at_sender=True)
        else:
            await UniMessage.text(msg).send(target=event, bot=bot, at_sender=True)
    except ActionFailed as e:
        logger.warning(f"发送消息给{event.get_user_id()}失败：{e}")
