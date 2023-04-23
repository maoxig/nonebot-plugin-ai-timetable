from .utils import *
from nonebot.plugin import PluginMetadata
from nonebot.params import RegexMatched, ArgStr, CommandArg, ArgPlainText
from nonebot.matcher import Matcher
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, MessageEvent, Message

logger.opt(colors=True).info(
    "已检测到软依赖<y>nonebot_plugin_apscheduler</y>, <g>开启定时任务功能</g>"
    if scheduler
    else "未检测到软依赖<y>nonebot_plugin_apscheduler</y>,<r>禁用定时任务功能</r>"
)

__plugin_meta__ = PluginMetadata(
    name="小爱课表",
    description="一键导入课表、查看课表、提醒上课、查询课程",
    usage=AiTimetable.ai_timetable__usage,
)


my_table = on_regex(r'^(小爱|我的|本周|下周)(课表)', priority=20, block=False)
new_table = on_command('导入课表', priority=20, block=False, aliases={'创建课表'})
table_help = on_command("课表帮助", priority=20, block=False,
                        aliases={"课表介绍", "课表怎么用"})
someday_table = on_regex(
    r'^(((今|明|昨|后)(天|日))|(星期|周)(一|二|三|四|五|六|日|天))(课表|的课|课程|((上|有)(什么|啥)课))', priority=20, block=False)
add_alock_someday = on_regex(
    r'^(订阅|提醒)((周|星期)(一|二|三|四|五|六|日|天))(课程|课表|的课)', priority=20, block=True)
add_alock_morningcalss = on_regex(
    r'^(订阅|提醒)早八', priority=20, block=True)
remove_alock_someday = on_regex(
    r'^(取消)(订阅|提醒)((周|星期)(一|二|三|四|五|六|日|天))(课程|的课|课表)', priority=20, block=False)
sub_class = on_command("订阅课程", priority=25, block=False, aliases={"提醒课程"})
remove_sub_class = on_command(
    "取消订阅课程", priority=25, block=False, aliases={"取消提醒课程"})
remove_alock_morningclass = on_command(
    "取消订阅早八", priority=20, block=False, aliases={"取消提醒早八"})
renew_table = on_command("更新本地课表", priority=20, block=False, aliases={'更新课表'})
send_next_class = on_command("上课", priority=20, block=False, aliases={"下节课"})
next_morningclass = on_command(
    "早八", priority=20, block=False, aliases={"明日早八", "明天早八"})


@table_help.handle()
async def _():
    """课表帮助"""
    if timetable_pic:
        await table_help.finish(MessageSegment.image(await md_to_pic(AiTimetable.ai_timetable__usage)))
    else:
        await table_help.finish(AiTimetable.ai_timetable__usage)


@my_table.handle()
async def _(event: MessageEvent, key: str = RegexMatched()):
    """获取本周/下周的课表"""
    uid = event.get_user_id()
    if uid in userdata:
        pic = await AiTimetable.my_table(uid=uid, key=key)
        await my_table.finish(MessageSegment.image(pic))
    else:
        await my_table.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)


@new_table.got('key', '请发送小爱课程表导出的链接,发送/取消以退出')
async def _(event: MessageEvent, key: str = ArgStr()):
    """更新本地的课表"""
    uid = event.get_user_id()
    url = str(key)
    if re.match(AiTimetable.base_url_re, url):  # 用户发送的链接匹配
        msg = await AiTimetable.new_table(uid=uid, base_url=key)
        await new_table.finish(msg)
    else:
        await new_table.finish("出错了,请检查链接是否正确", at_sender=True)


@someday_table.handle()
async def _(event: MessageEvent, key: str = RegexMatched()):
    """发送某天的课表"""
    uid = event.get_user_id()
    if uid not in userdata:
        await someday_table.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if timetable_pic:
            pic = await AiTimetable.someday_table(uid=uid, key=key)
            await someday_table.finish(MessageSegment.image(pic))
        else:
            await someday_table.finish(await AiTimetable.someday_table(uid=uid, key=key))


@renew_table.handle()  # 更新本地课表
async def _(event: MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await renew_table.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        msg = await AiTimetable.renew_table(uid=uid)
        await renew_table.finish(msg, at_sender=True)


@send_next_class.handle()  # 发送本节课、以及下节课信息
async def _(event: MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await send_next_class.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        msg = "现在时间是"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg += AiTimetable.now_class(uid)
        msg += AiTimetable.next_class(uid)
        await send_next_class.finish(msg, at_sender=True)


@next_morningclass.handle()
async def _(bot: Bot, event: MessageEvent):
    """发送早八"""
    uid = event.get_user_id()
    if uid not in userdata:
        await send_next_class.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        await AiTimetable.post_alock_morningclass(uid=uid, bot=bot, event=event)

#-----------以下为定时任务----------------#


@add_alock_someday.handle()
async def _(bot: Bot, event: MessageEvent, key: str = RegexMatched()):
    """订阅课表"""
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (AiTimetable.weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock"+str(send_day))):
                await add_alock_someday.finish("出错了！你好像已经订阅过这天的课表了呢", at_sender=True)
            scheduler.add_job(AiTimetable.post_alock, "cron", hour=timetable_alock_someday, second=random.randint(0, 60), id=str(
                uid+"post_alock"+str(send_day)), day_of_week=send_day,kwargs={"key": key, "uid": uid, "bot": bot, "event": event})
            await add_alock_someday.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_someday.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)


@remove_alock_someday.handle()
async def _(bot: Bot, event: MessageEvent, key: str = RegexMatched()):
    """删除订阅课表"""
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_someday.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            send_day = (AiTimetable.weekday_int(key)+5) % 7
            if scheduler.get_job(str(uid+"post_alock"+str(send_day))):
                scheduler.remove_job(str(uid+"post_alock"+str(send_day)))
                await remove_alock_someday.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_someday.finish("出错了,好像没有订阅过这天的课表呢", at_sender=True)
        else:
            await remove_alock_someday.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)

#-----------以下为订阅早八----------------#


@add_alock_morningcalss.handle()
async def _(bot: Bot, event: MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass")):
                await add_alock_morningcalss.finish("出错了！你好像已经订阅过早八提醒了呢", at_sender=True)
            scheduler.add_job(AiTimetable.post_alock_morningclass, "cron", hour=timetable_alock_8, second=random.randint(
                0, 60), id=str(uid+"post_alock_morningclass"), kwargs={"uid": uid, "bot": bot, "event": event})
            await add_alock_morningcalss.finish("定时提醒添加成功！", at_sender=True)
        else:
            await add_alock_morningcalss.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)


@remove_alock_morningclass.handle()
async def _(event: MessageEvent):
    uid = event.get_user_id()
    if uid not in userdata:
        await add_alock_morningcalss.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            if scheduler.get_job(str(uid+"post_alock_morningclass")):
                scheduler.remove_job(str(uid+"post_alock_morningclass"))
                await remove_alock_morningclass.finish("定时提醒删除成功！", at_sender=True)
            else:
                await remove_alock_morningclass.finish("出错了,好像没有订阅过早八呢", at_sender=True)
        else:
            await remove_alock_morningclass.finish("apscheduler插件未载入,无法删除定时提醒", at_sender=True)


@sub_class.handle()
async def _(matcher:Matcher,args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("text",args)


@sub_class.got("text", prompt="请告诉我课程名~")
async def sub_handler(bot: Bot, event: MessageEvent,text:str=ArgPlainText()):
    uid = event.get_user_id()
    if uid not in userdata:
        await sub_class.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            msg = AiTimetable.sub_class(uid=uid, key=text, event=event, bot=bot)
            await sub_class.finish(msg, at_sender=True)
        else:
            await sub_class.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)


@remove_sub_class.handle()
async def _(matcher:Matcher,args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("text",args)


@remove_sub_class.got("text", prompt="请告诉我课程名~")
async def remove_sub_handler(event: MessageEvent,text:str=ArgPlainText()):
    uid = event.get_user_id()
    if uid not in userdata:
        await remove_sub_class.finish('你还没有导入课表,发送/导入课表来导入吧！', at_sender=True)
    else:
        if scheduler:
            msg = AiTimetable.remove_sub_class(uid=uid, key=text)
            await remove_sub_class.finish(msg, at_sender=True)
        else:
            await remove_sub_class.finish("apscheduler插件未载入,无法添加定时提醒", at_sender=True)
