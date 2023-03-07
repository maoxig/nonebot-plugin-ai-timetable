import os
import json
import time
import datetime
from nonebot import logger


def log_debug(command: str, info: str):
    logger.opt(colors=True).debug(f'<u><y>[{command}]</y></u>{info}')


res_url_re = r'^(https://i\.ai\.mi\.com/course-multi/table\?)*(ctId=)\d+(&userId=)\d*[1-9]\d*(&deviceId=)[0-9a-zA-Z]*(&sourceName=course-app-browser)'
base_url_re = r'https://cdn\.cnbj1\.fds\.api\.mi-img.com/miai-fe-aischedule-wx-redirect-fe/redirect.html\?linkToken=.+'



def write_data() -> None:# 写入用户信息
    with open("data/ai_timetable/userdata.json", 'w', encoding='utf-8') as f:
        json.dump(userdata, f)


# 读取用户信息
if os.path.exists("data/ai_timetable/userdata.json"):
    with open("data/ai_timetable/userdata.json", 'r', encoding='utf-8') as f:
        userdata = json.load(f)
else:
    if not os.path.exists("data/ai_timetable"):
        os.makedirs("data/ai_timetable")
    userdata = {}
    write_data()



# 读取用户url


def write_table() -> None:
    with open("data/ai_timetable/usertable.json", 'w', encoding='utf-8') as f:
        json.dump(usertable, f,ensure_ascii=False)


if os.path.exists("data/ai_timetable/usertable.json"):
    with open("data/ai_timetable/usertable.json", 'r', encoding='utf-8') as f:
        usertable = json.load(f)
else:
    if not os.path.exists("data/ai_timetable"):
        os.makedirs("data/ai_timetable")
    usertable = {}
    write_table()



def weekday_int(key)-> int:#把中文周数转换成整数
    cn2an = {'今': datetime.datetime.now().weekday()+1, '明': datetime.datetime.now().weekday()+2, '昨': datetime.datetime.now().weekday(), '后': datetime.datetime.now().weekday()+3, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六':6,'日':7,'天':7}
    for i in cn2an:
        if i in key:
            return cn2an[i]
    return 7
    
    
        
def table_msg(key,uid)->str:
    presentweek = int((time.time() - int(
        usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1  # 这里算出的结果是小数,转换成整数
    someday = weekday_int(key)
    # 日期变时周数也会变
    if someday < 0:
        someday += 7
        presentweek -= 1
    elif someday > 7:
        someday -= 7
        presentweek += 1
        # 构造发送的信息
    msg = '你要的课表来咯喵:\n'
    for courses in usertable[uid]["data"]["courses"]:
        if(courses["day"] == someday) and (str(presentweek) in courses["weeks"].split(',')):
            sections=courses["sections"].split(",")
            startsection=int(sections[0])
            endsection=int(sections[-1])
            starttime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                startsection-1]["s"]
            endtime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                endsection-1]["e"]
            msg = msg+'\n'+'#'+starttime+'-'+endtime+'\n'+courses["name"]+"\n@"+courses["position"]
    return msg            

def now_class(uid)->str:#这里构造出当前课程的信息
    presentweek = int((time.time() - int(
    usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1
    today= weekday_int("今")
    now_section=0
    now_time=datetime.datetime.now().strftime("%H:%M")
    msg=""
    for course_time in  eval(usertable[uid]["data"]["setting"]["sectionTimes"]):
            if course_time["s"]<now_time<course_time["e"]:
                now_section=course_time["i"]
    if now_section:
        count=0
        for courses in usertable[uid]["data"]["courses"]:
            if (str(presentweek) in courses["weeks"].split(",")) and (today==courses["day"]) and (str(now_section) in courses["sections"].split(",")):
                    msg+="\n你现在在上的课程信息如下喵:\n"+courses["name"]+"\n@"+courses["position"]+"\n"+courses["teacher"]
                    count+=1
        if not count:
            msg+="\n你现在没有课呢,空闲时间好好休息吧喵~"
        else:
            pass
                       
    else:
        msg+="\n你现在没有课呢,空闲时间好好休息吧喵~"
    return msg

              
    
    
def next_class(uid)->str:
    now_time=datetime.datetime.now().strftime("%H:%M")
    presentweek = int((time.time() - int(
    usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1
    today= weekday_int("今")
    for courses in usertable[uid]["data"]["courses"]:
        if str(presentweek) in courses["weeks"].split(",") and today==courses["day"] :#遍历当前天的所有存在的课
            next_class_section=int(courses["sections"].split(",")[0])
            next_class_section_end=int(courses["sections"].split(",")[-1])
            if eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section-1]["s"]>now_time:
                return "\n你今天的下一节课程信息为：\n"+eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section-1]["s"]+"-"+eval(usertable[uid]["data"]["setting"]["sectionTimes"])[next_class_section_end-1]["e"]+"\n"+courses["name"]+"\n@"+courses["position"]+"\n"+courses["teacher"]
            #这里是因为之前已经按照顺序排好了课程,所以第一个找到的就是下节课
    return "\n你今天接下来没有课了呢,好好享受吧喵~"
                