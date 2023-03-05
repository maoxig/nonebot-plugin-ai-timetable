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

cn2an = {'今': datetime.datetime.now().weekday()+1, '明': datetime.datetime.now().weekday()+2, '昨': datetime.datetime.now().weekday(), '后': datetime.datetime.now().weekday()+3, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六':6,'日':7,'天':7}

def weekday_int(key)-> int:#把中文周数转换成整数
    for i in cn2an:
        if i in key:
            return cn2an[i]
    return 7
    
    
        
def table_msg(key,uid)->str:
    presentweek = int((time.time() - int(
        usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)+1  # 这里算出的结果是小数，转换成整数
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
    for i in range(len(usertable[uid]["data"]["courses"])):
        if(usertable[uid]["data"]["courses"][i]["day"] == someday) and (str(presentweek) in usertable[uid]["data"]["courses"][i]["weeks"].split(',')):
            sections = usertable[uid]["data"]["courses"][i]["sections"].split(
                ",")
            startsection = int(sections[0])
            endsection = int(sections[-1])
            starttime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                startsection-1]["s"]
            endtime = eval(usertable[uid]["data"]["setting"]["sectionTimes"])[
                endsection-1]["e"]
            msg = msg+'\n'+'#'+starttime+'-'+endtime+'\n' + \
                usertable[uid]["data"]["courses"][i]["name"] + '\n@' + \
                usertable[uid]["data"]["courses"][i]["position"]
    return msg            



