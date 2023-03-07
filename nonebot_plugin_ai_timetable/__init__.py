import httpx
import re
from .utils import*
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.params import RegexMatched, ArgStr
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, MessageEvent, GroupMessageEvent,PrivateMessageEvent
from nonebot import require, get_bot
require('nonebot_plugin_htmlrender')
require('nonebot_plugin_apscheduler')
from nonebot_plugin_htmlrender import get_new_page
from nonebot_plugin_apscheduler import scheduler
logger.opt(colors=True).info(
    "已检测到软依赖<y>nonebot_plugin_apscheduler</y>, <g>开启定时任务功能</g>"
    if scheduler
    else "未检测到软依赖<y>nonebot_plugin_apscheduler</y>,<r>禁用定时任务功能</r>"
)
__plugin_meta__ = PluginMetadata(
    name="小爱课表",
    description="一键导入课表、查看课表、提醒上课、查询课程",
    usage="课表帮助",
)
mytable = on_regex(r'^(小爱|我的|本周|下周)(课表)', priority=20, block=False)
newtable = on_command('导入课表', priority=20, block=False, aliases={'创建课表'})
tablehelp = on_command("课表帮助", priority=20, block=False,
                       aliases={"课表介绍", "课表怎么用"})
someday_table = on_regex(
    r'^(((今|明|昨|后)(天|日))|(星期|周)(一|二|三|四|五|六|日|天))(课表|课程|((上|有)(什么|啥)课))', priority=20, block=False)
add_alock_someday = on_regex(
    r'^(订阅|提醒)((周|星期)(一|二|三|四|五|六|日|天))(课程|课表)', priority=20, block=False)
add_alock_morningcalss = on_regex(
    r'^(订阅|提醒)早八', priority=20, block=False)
remove_alock_someday = on_regex(
    r'^(取消)(订阅|提醒)((周|星期)(一|二|三|四|五|六|日|天))(课程|课表)', priority=20, block=False)
remove_alock_morningclass=on_command("取消订阅早八",priority=20,block=False,aliases={"取消提醒早八"})
renew_table=on_command("更新本地课表",priority=20,block=False,aliases={'更新课表'})
send_next_class=on_command("上课",priority=20,block=False,aliases={"下节课"})

@tablehelp.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    await tablehelp.finish(__usage__)
__usage__ = "@小爱课表帮助:\n#我的/本周课表:获取本周课表,也可以是下周\n#导入课表:使用小爱课程表分享的链接一键导入\n#某日课表:获取某日课表,如今日课表、周一课表\n#更新课表:更新本地课表信息\n#订阅/取消订阅xx课表:可以订阅某天(如周一)的课表,在前一天晚上10点推送\n#订阅/取消订阅早八:订阅所有早八,在前一天晚上发出提醒\n#上课/下节课:获取当前课程信息以及今天内的下节课"


@mytable.handle()  # 本/下 周完整课表
async def _(bot: Bot, event: MessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    if uid in userdata:
        async with get_new_page(viewport={"width": 1000, "height": 1200}) as page:
            page.on("response", lambda response: geturl(response))
            await page.goto(userdata[uid], wait_until='networkidle')
            # 这里使小爱课程表的导入按钮隐藏,防止遮挡课表
            await page.evaluate('var t = document.querySelector("#root>div>div.importSchedule___UjEKt>div.footer___1iAis.toUp___2mciB"); t.style.display = "none"')
            if '下' in key:  # 如果命令中有下字,就点击下一周的按钮
                await page.click("#schedule-view > div.header___26sI1 > div.presentWeek___-o65e > div.rightBtn___2ZhSY")
            pic = await page.screenshot(full_page=True, path="./mytable.png")
            await mytable.finish(MessageSegment.image(pic))

    else:
        await mytable.finish('你还没有导入课表,发送\\导入课表来导入吧！', at_sender=True)
# 导入课表

res_url = "寄"


def geturl(response):
    global res_url
    res_url = str(response.url) if re.match(
        res_url_re, response.url) else res_url


@newtable.got('key', '请发送小爱课程表导出的链接,发送\\取消以退出')  # 导入课表
async def _(matcher: Matcher, bot: Bot, event: MessageEvent, key: str = ArgStr()):
    uid = event.get_user_id()
    url = str(key)
    log_debug("导入url", url)
    if re.match(base_url_re, url):  # 用户发送的链接匹配
        async with get_new_page(viewport={"width": 1000, "height": 1200}) as page:
            page.on("response", lambda response: geturl(response))
            await page.goto(url, wait_until='networkidle')
            global res_url
            log_debug("response.url", res_url)
            async with httpx.AsyncClient() as r:
                res = await r.get(res_url)
                usertable.update({uid: res.json()})
                usertable[uid]["data"]["courses"].sort(
                    key=lambda x: int(x["sections"][0]))  # 这里要对课表排序,否则打印课表时不会按时间顺序来
                write_table()
        if uid in userdata:  # 这里保存的是小爱课程表分享的链接,就可以定时通过这里的链接更新本地课表,但是还不清楚链接是否会失效
            userdata.update({uid: url})
            write_data()
            await newtable.finish("你已经导入过课表了喵,咱帮你更新课表数据了", at_sender=True)
        elif uid not in userdata:
            userdata.update({uid: url})
            write_data()
            await newtable.finish("成功导入课表喵！快发送课表帮助来查看功能吧！", at_sender=True)
    else:
        await newtable.finish("出错了,请检查链接是否正确", at_sender=True)


@someday_table.handle()  # 某天的课表
async def _(matcher: Matcher, bot: Bot, event: MessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    if uid not in userdata:
        await someday_table.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        await someday_table.finish(table_msg(key, uid), at_sender=True)

@renew_table.handle()#更新本地课表
async def _(matcher:Matcher,bot:Bot,event:MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await renew_table.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        async with get_new_page(viewport={"width": 1000, "height": 1200}) as page:
            page.on("response", lambda response: geturl(response))
            await page.goto(userdata[uid], wait_until='networkidle')
            global res_url
            log_debug("response.url", res_url)
            async with httpx.AsyncClient() as r:
                res = await r.get(res_url)
                usertable.update({uid: res.json()})
                usertable[uid]["data"]["courses"].sort(
                    key=lambda x: int(x["sections"][0]))  # 这里要对课表排序,否则打印课表时不会按时间顺序来
                write_table()
        await renew_table.finish("本地课表已更新喵！", at_sender=True)

@send_next_class.handle()#发送本节课、以及下节课信息
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await send_next_class.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:        
        msg="现在时间是"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg+=now_class(uid)+next_class(uid)
        await send_next_class.finish(msg,at_sender=True)
    
#-----------以下为定时任务----------------#
@add_alock_someday.handle()#群内订阅课表
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    gid = event.group_id
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock_group"+str(send_day))):
                await add_alock_someday.finish("出错了喵！你好像已经订阅过这天的课表了呢", at_sender=True)
            scheduler.add_job(post_alock, "cron", hour=22, id=str(
                uid+"post_alock_group"+str(send_day)), args=[key, uid, gid], day_of_week=send_day)
            await add_alock_someday.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_someday.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)

@add_alock_someday.handle()#私聊订阅课表
async def _(matcher: Matcher, bot: Bot, event: PrivateMessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock_private"+str(send_day))):
                await add_alock_someday.finish("出错了喵！你好像已经订阅过这天的课表了呢", at_sender=True)
            scheduler.add_job(post_alock, "cron", hour=22, id=str(
                uid+"post_alock_private"+str(send_day)), args=[key, uid,None], day_of_week=send_day)
            await add_alock_someday.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_someday.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)

@remove_alock_someday.handle()#群内删除订阅课表
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock_group"+str(send_day))):
                scheduler.remove_job(str(uid+"post_alock_group"+str(send_day)))
                await remove_alock_someday.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_someday.finish("出错了,好像没有订阅过这天的课表呢", at_sender=True)
        else:
            await remove_alock_someday.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)

@remove_alock_someday.handle()#私聊删除订阅课表
async def _(matcher: Matcher, bot: Bot, event: PrivateMessageEvent, key: str = RegexMatched()):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock_private"+str(send_day))):
                scheduler.remove_job(str(uid+"post_alock_private"+str(send_day)))
                await remove_alock_someday.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_someday.finish("出错了,好像没有订阅过这天的课表呢", at_sender=True)
        else:
            await remove_alock_someday.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)

#-----------以下为订阅早八----------------#
@add_alock_morningcalss.handle()#群聊订阅早八
async def _(matcher:Matcher,bot:Bot,event:GroupMessageEvent):
    uid=event.get_user_id()
    gid = event.group_id
    
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass_group")):
                await add_alock_morningcalss.finish("出错了喵！你好像已经订阅过早八提醒了呢", at_sender=True)
            scheduler.add_job(post_alock_morningclass, "cron", hour=21,id=str(uid+"post_alock_morningclass_group"), args=[uid, gid])
            await add_alock_morningcalss.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_morningcalss.finish("apscheduler插件未载入,无法添加定时提醒喵", at_sender=True)

@add_alock_morningcalss.handle()#私聊订阅早八
async def _(matcher:Matcher,bot:Bot,event:PrivateMessageEvent):
    uid=event.get_user_id()
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表喵,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass_private")):
                await add_alock_morningcalss.finish("出错了喵！你好像已经订阅过早八提醒了呢", at_sender=True)
            scheduler.add_job(post_alock_morningclass, "cron", hour=21,id=str(uid+"post_alock_morningclass_private"), args=[uid, None])
            await add_alock_morningcalss.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_morningcalss.finish("apscheduler插件未载入,无法添加定时提醒喵", at_sender=True)


@remove_alock_morningclass.handle()#群移除早八
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass")):
                scheduler.remove_job(str(uid+"post_alock_morningclass"))
                await remove_alock_morningclass.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_morningclass.finish("出错了,好像没有订阅过早八呢", at_sender=True)
        else:
            await remove_alock_morningclass.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)
            
@remove_alock_morningclass.handle()#私聊移除早八
async def _(matcher: Matcher, bot: Bot, event: PrivateMessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表,发送\\导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass")):
                scheduler.remove_job(str(uid+"post_alock_morningclass"))
                await remove_alock_morningclass.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_morningclass.finish("出错了,好像没有订阅过早八呢", at_sender=True)
        else:
            await remove_alock_morningclass.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)


async def post_alock(*args):#发送某天的课表消息
    key = args[0]
    uid = args[1]
    if '一' in key:
        key = "明日课表"  # 发送周一课表时是周日,所以要发送的其实是明日课表
    msg = table_msg(key=key, uid=uid)
    if not args[2]:
        send_id = args[1]
        message_type="private"
        await get_bot().send_msg(message_type=message_type,user_id=send_id,message=MessageSegment.at(int(uid))+msg)
    else:
        message_type="group"
        send_id=args[2]
        await get_bot().send_msg(message_type=message_type,group_id=send_id,message=MessageSegment.at(int(uid))+msg)

    
    


async def post_alock_morningclass(*args):#发送第二天的早八消息
    uid=args[0]
    someday=weekday_int("明")
    someweek=int((time.time() - int(
        usertable[uid]["data"]["setting"]['startSemester'][0:10]))//604800)
    if someday==8:#星期天发送时时第二天是星期一,周数加1
        someday=1
        someweek=someweek+1  
    count=0
    msg="我来了喵!"
    for courses in usertable[uid]["data"]["courses"]:
        if (courses["day"] == someday) and str(someweek) in courses["weeks"].split(",") and "1" in courses["sections"].split(","):
            count+=1
            msg+='\n'+courses["name"] + '\n@' + courses["position"]+'\n'+courses["teacher"]
    if count==0:
         msg+="\n你明天没有早八呢！享受夜生活吧！"
    else:
        msg+=f"\n你明天有{count}节早八呢！今晚早点休息吧！"
    if not args[1]:
        send_id=uid
        await get_bot().send_msg(user_id=send_id, message=MessageSegment.at(int(uid))+msg)
    else:
        send_id=args[1]
        await get_bot().send_msg(group_id=send_id, message=MessageSegment.at(int(uid))+msg)



    

