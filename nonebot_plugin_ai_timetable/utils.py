from nonebot.adapters.onebot.v11 import ActionFailed,MessageSegment
from nonebot import get_driver, logger, require
require('nonebot_plugin_htmlrender')
require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_htmlrender import get_new_page, md_to_pic
import os
import re
import json
import time
import datetime
import httpx
import random


config = get_driver().config
timetable_pic: bool = getattr(config, "timetable_pic", True)
timetable_alock_someday: int = getattr(config, "timetable_alock_someday", 22)
timetable_alock_8: int = getattr(config, "timetable_alock_8", 21)
timetable_send_time:float=getattr(config,"timetable_send_time",0.5)

if os.path.exists("data/ai_timetable/userdata.json"):
    with open("data/ai_timetable/userdata.json", 'r', encoding='utf-8') as f:
        userdata = json.load(f)
else:
    if not os.path.exists("data/ai_timetable"):
        os.makedirs("data/ai_timetable")
    userdata = {}
    with open("data/ai_timetable/userdata.json", 'w', encoding='utf-8') as f:
        json.dump(userdata, f)
    
if os.path.exists("data/ai_timetable/usertable.json"):
    with open("data/ai_timetable/usertable.json", 'r', encoding='utf-8') as f:
        usertable = json.load(f)
else:
    if not os.path.exists("data/ai_timetable"):
        os.makedirs("data/ai_timetable")
    usertable = {}
    with open("data/ai_timetable/usertable.json", 'w', encoding='utf-8') as f:
        json.dump(usertable, f, ensure_ascii=False)
        



class AiTimetable:
    res_url_re = r'^(https://i\.ai\.mi\.com/course-multi/table\?)*(ctId=)\d+(&userId=)\d*[1-9]\d*(&deviceId=)[0-9a-zA-Z]*(&sourceName=course-app-browser)'
    base_url_re = r'https://cdn\.cnbj1\.fds\.api\.mi-img.com/miai-fe-aischedule-wx-redirect-fe/redirect.html\?linkToken=.+'

    ai_timetable__usage = "## 小爱课表帮助:\n- 我的/本周课表: 获取本周课表,也可以是下周\n- 导入课表: 使用小爱课程表分享的链接一键导入\n- 某日课表: 获取某日课表,如今日课表、周一课表\n- 更新课表: 更新本地课表信息,如果线上修改过小爱课表,发送该指令即可更新本地课表\n- 订阅/取消订阅xx课表: 可以订阅某天(如周一)的课表,在前一天晚上10点推送\n- 订阅/取消订阅早八: 订阅所有早八,在前一天晚上发出提醒\n- 订阅/取消订阅课程+课程名：订阅某节课程\n- 上课/下节课: 获取当前课程信息以及今天以内的下节课信息\n- 早八|明日早八: 查询明天的早八"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
    }
    def __init__(self, uid) -> None:
        self.uid=uid

    @staticmethod
    def weekday_int(key) -> int:
        """中文日期转数字"""
        cn2an = {'今': datetime.datetime.now().weekday()+1, '明': datetime.datetime.now().weekday()+2, '昨': datetime.datetime.now().weekday(),
                '后': datetime.datetime.now().weekday()+3, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7, '天': 7}
        for i in cn2an:
            if i in key:
                return cn2an[i]
        return 7

    @classmethod
    def next_class(cls, uid) -> str:
        """
        获得下节课程信息
        """
        now_time = datetime.datetime.now().strftime("%H:%M")
        presentweek = int((time.time() - int(
            usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1
        today = cls.weekday_int("今")
        for courses in usertable[uid]["data"]["courses"]:
            # 遍历当前天的所有存在的课
            if str(presentweek) in courses["weeks"].split(",") and today == courses["day"]:
                next_class_section = int(courses["sections"].split(",")[0])
                next_class_section_end = int(
                    courses["sections"].split(",")[-1])
                if eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section-1]["s"] > now_time:
                    return "\n你今天的下一节课程信息为：\n"+eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section-1]["s"]+"-"+eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section_end-1]["e"]+"\n"+courses["name"]+"\n@"+courses["position"]+"\n"+courses["teacher"]
                #这里是因为之前已经按照顺序排好了课程,所以第一个找到的就是下节课
        return "\n你今天接下来没有课了呢,好好休息吧"
    @classmethod
    def now_class(cls, uid) -> str:
        """ 
        构造出当前课程信息
        """
        presentweek = int((time.time() - int(
            usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1
        today = cls.weekday_int("今")
        now_section = 0
        now_time = datetime.datetime.now().strftime("%H:%M")
        msg = ""
        for course_time in eval(usertable[uid]["data"]["setting"]["sectionTimes"]):
            if course_time["s"] < now_time < course_time["e"]:
                now_section = course_time["i"]
        if now_section:
            count = 0
            for courses in usertable[uid]["data"]["courses"]:
                if (str(presentweek) in courses["weeks"].split(",")) and (today == courses["day"]) and (str(now_section) in courses["sections"].split(",")):
                    msg += "\n你现在在上的课程信息如下:\n"+eval(usertable[uid]["data"]["setting"]["sectionTimes"])[int(courses["sections"].split(",")[0])-1]["s"]+"-"+eval(
                        usertable[uid]["data"]["setting"]["sectionTimes"])[int(courses["sections"].split(",")[-1])-1]["e"]+'\n'+courses["name"]+"\n@"+courses["position"]+"\n"+courses["teacher"]
                    count += 1
            if not count:
                msg += "\n你现在没有课呢,空闲时间好好休息吧"
        else:
            msg += "\n你现在没有课呢,空闲时间好好休息吧"
        return msg
    @classmethod
    def table_msg(cls, key, uid) -> str:
        """
        构造今日课表信息
        """
        presentweek = int((time.time() - int(
            usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1  # 这里算出的结果是小数,转换成整数
        someday = cls.weekday_int(key)
        # 日期变时周数也会变
        if someday < 0:
            someday += 7
            presentweek -= 1
        elif someday > 7:
            someday -= 7
            presentweek += 1
            # 构造发送的信息
        if timetable_pic:
            msg = "|时间|课程|地点|\n| :-----| :----: | :----: |"
        else:
            msg = "课表来了~"
        for courses in usertable[uid]["data"]["courses"]:
            if(courses["day"] == someday) and (str(presentweek) in courses["weeks"].split(',')):

                sections = courses["sections"].split(",")
                startsection = int(sections[0])
                endsection = int(sections[-1])
                starttime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                    startsection-1]["s"]
                endtime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                    endsection-1]["e"]
                if timetable_pic:
                    msg = msg+'\n'+'|'+starttime+'-'+endtime + \
                        '|'+courses["name"]+'|'+courses["position"]

                else:
                    msg = msg+'\n'+starttime+'-'+endtime+'\n' + \
                        courses["name"]+"\n@"+courses["position"]+'\n'
        return msg

    @staticmethod
    async def my_table(uid, key):
        """
        获取本周或者下周课表
        """
        try:
            async with get_new_page(viewport={"width": 1000, "height": 1000}) as page:
                await page.goto(userdata[uid][0],wait_until="networkidle")
                # 这里使小爱课程表的导入按钮隐藏,防止遮挡课表
                await page.evaluate('var t = document.querySelector("#root>div>div.importSchedule___UjEKt>div.footer___1iAis.toUp___2mciB"); t.style.display = "none"')
                if '下' in key:  # 如果命令中有下字,就点击下一周的按钮
                    await page.click("#schedule-view > div.header___26sI1 > div.presentWeek___-o65e > div.rightBtn___2ZhSY")
                pic = await page.screenshot(full_page=True,type="jpeg",quality=70)
                return pic
        except Exception as e:
            logger.warning(f"获取课表时出错：{e}")
    @classmethod
    async def response_listener(cls,base_url, uid, response):
        """监听请求"""  
        if re.match(cls.res_url_re,response.url):
                userdata.update({uid:(base_url,response.url)})
    @staticmethod
    async def write_data() -> None:
        """写入用户数据"""
        with open("data/ai_timetable/userdata.json", 'w', encoding='utf-8') as f:
            json.dump(userdata, f)

    @staticmethod
    async def write_table() -> None:
        """写入用户课表"""
        with open("data/ai_timetable/usertable.json", 'w', encoding='utf-8') as f:
            json.dump(usertable, f, ensure_ascii=False)
    @classmethod
    async def new_table(cls,uid,base_url)->str:
        """更新课表"""
        try:
            async with get_new_page(viewport={"width": 1000, "height": 1200}) as page:
                page.on("response", lambda response: cls.response_listener(response=response,uid=uid,base_url=base_url))
                await page.goto(url=base_url,wait_until="networkidle")
                if uid in userdata:
                    async with httpx.AsyncClient() as client:
                        res=await client.get(userdata[uid][1],headers=cls.headers)
                        usertable.update({uid:res.json()})
                        #更新课表
                        usertable[uid]["data"]["courses"].sort(
                    key=lambda x: int(x["sections"].split(",")[0]))
                        #对课表排序
                        await cls.write_table()
                        await cls.write_data()
                        return "成功导入课表！"
                else:
                    return "出错了，可能是没有在小爱课表内登录账户"
        except Exception as e:
            logger.warning(f"获取课表时出错：{e}")
            return f"出错了：{e}"
            
    @classmethod
    async def renew_table(cls,uid):
        """
        用户已有url的情况下更新本地课表
        """
        try:
            async with httpx.AsyncClient() as client:
                res=await client.get(userdata[uid][1],headers=cls.headers)
                usertable.update({uid:res.json()})
                        #更新课表
                usertable[uid]["data"]["courses"].sort(
                    key=lambda x: int(x["sections"].split(",")[0]))
                        #对课表排序
                await cls.write_table()
                await cls.write_data()
                return "更新成功"
        except Exception as e:
            return f"{e}"

    @classmethod
    async def someday_table(cls,uid,key): 
        """某天的课表"""
        try:
            msg=cls.table_msg(uid=uid,key=key)
            if not timetable_pic:
                return msg
            else:
                pic=await md_to_pic(md=msg)
                return pic
        except Exception as e:
            logger.warning(f"出错了，出错原因：{e}")
    @classmethod
    async def post_alock_morningclass(cls,**kwargs):
        """发送早八消息"""
        uid,bot,event=kwargs["uid"],kwargs["bot"],kwargs["event"]
        try:
            someday=cls.weekday_int("明")
            someweek=int((time.time() - int(
                usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)
            if someday==8:#星期天发送时时第二天是星期一,周数加1
                someday=1
                someweek=someweek+1  
            count=0
            msg = "现在时间是"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for courses in usertable[uid]["data"]["courses"]:
                if (courses["day"] == someday) and str(someweek) in courses["weeks"].split(",") and "1" in courses["sections"].split(","):
                    count+=1
                    msg+='\n'+courses["name"] + '\n@' + courses["position"]+'\n'+courses["teacher"]
            if count==0:
                msg+="\n你明天没有早八呢！享受夜生活吧！"
            else:
                msg+=f"\n你明天有{count}节早八呢！今晚早点休息吧！"
            await bot.send(event,message=msg,at_sender=True)
        except ActionFailed as e:
            logger.warning(f"发送消息给{event.get_user_id()}失败：{e}")
    @classmethod
    async def post_alock(cls,**kwargs):
        """发送第二天课程消息"""
        key,uid,bot,event=kwargs["key"],kwargs["uid"],kwargs["bot"],kwargs["event"]
        if "一" in key:
            key="明"
        msg=cls.table_msg(key=key,uid=uid)
        try:
            if timetable_pic:
                pic=await md_to_pic(md=msg)
                await bot.send(event,MessageSegment.image(file=pic),at_sender=True)
            else:
                await bot.send(event,message=msg,at_sender=True)
        except ActionFailed as e:
            logger.warning(f"发送消息失败：{e}")
            
    @classmethod
    def sub_class(cls,**kwargs)->str:
        """订阅一周内所有课程名中有key的课程"""
        uid,key,bot,event=kwargs["uid"],kwargs["key"],kwargs["bot"],kwargs["event"]
        i=0
        for courses in usertable[uid]["data"]["courses"]:
            # 遍历当前天的所有存在的课
            if key in courses["name"]:
                i+=1
                if scheduler.get_job(job_id=uid+courses["name"]+str(i)):
                    continue
                else:
                    class_section = int(courses["sections"].split(",")[0])
                    starttime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[class_section-1]["s"]#获取课程开始时间
                    hours = int(timetable_send_time)#从设置中获取提前的小时数
                    minutes = int((timetable_send_time - hours) * 60)#从设置中获取提前的分钟数
                    time_obj = datetime.datetime.strptime(starttime, "%H:%M")#将字符串转换为datetime
                    new_time_obj = time_obj - datetime.timedelta(hours=hours, minutes=minutes)#进行时间的运算
                    sub_hour=new_time_obj.hour#获取发送时间的小时
                    sub_minute=new_time_obj.minute#获取发送时间的分钟
                    sub_day=courses["day"]-1
                    scheduler.add_job(cls.send_sub_class,"cron",id=uid+courses["name"]+str(i), hour=sub_hour, minute=sub_minute, day_of_week=sub_day, second=random.randint(0, 60),kwargs={"uid": uid, "bot": bot, "event": event,"course":{"name":courses["name"],"position":courses["position"],"teacher":courses["teacher"]}})
        return f"成功订阅了{i}节课~"
    
    @classmethod
    def remove_sub_class(cls,**kwargs):
        uid,key=kwargs["uid"],kwargs["key"]
        i=0
        for courses in usertable[uid]["data"]["courses"]:
            # 遍历当前天的所有存在的课
            if key in courses["name"]:
                i+=1
                if scheduler.get_job(job_id=uid+courses["name"]+str(i)):
                    scheduler.remove_job(job_id=uid+courses["name"]+str(i))
                else:
                    continue
        return f"成功取消订阅{i}节课~"
    @classmethod
    async def send_sub_class(cls,**kwargs):
        """发送订阅课程"""
        uid,bot,event,course=kwargs["uid"],kwargs["bot"],kwargs["event"],kwargs["course"]
        try:
            msg = "现在时间是"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg+="\n还有{}小时，你订阅的课程就要开始啦！课程信息如下:\n{}\n{}\n{}".format(timetable_send_time,course["name"],course["position"],course["teacher"])
            await bot.send(event, message=MessageSegment.at(uid)+msg, at_sender=True)
        except ActionFailed as e:
            logger.warning(f"发送消息给{event.get_user_id()}失败：{e}")
        
        
        