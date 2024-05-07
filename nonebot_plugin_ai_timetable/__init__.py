from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.params import (
    ArgStr,
    CommandArg,
    ArgPlainText,
    Depends,
)
from nonebot.matcher import Matcher
from nonebot import on_command, on_regex, require, logger, get_plugin_config
from nonebot.adapters import Message, Event, Bot


require("nonebot_plugin_alconna")
require("nonebot_plugin_orm")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_alconna import UniMessage

from .config import Config
from .manager import (
    check_user,
    check_base_url,
    build_table,
    send_table,
    update_table,
    update_offline_table_by_uid
)
from .reminder import (
    check_scheduler,
    add_reminders,
    remove_reminders,
    query_reminders_by_uid,
)

__ai_timetable__usage__ = "## 小爱课表帮助:\n- 课表帮助：获取本条帮助\n- 导入课表: 使用小爱课程表分享的链接一键导入\n- 更新课表：导入课表后，若云端课表有修改，可直接更新本地课表\n-  查询课表+[参数]：查询[参数]的课表，参数支持[本周/下周、周x、昨天/今天/明天/后天、早八、课程名、下节课]\n- 添加课程提醒+[参数]：参数支持[周x、早八、课程名]\n- 删除课程提醒+[参数]：参数支持[全部、周x、早八、课程名]\n- 查看课程提醒：查看当前已经添加的课程提醒"


__plugin_meta__ = PluginMetadata(
    name="小爱课表",
    description="一键导入课表、查看课表、提醒上课、查询课程，使用/课表帮助查看指令列表",
    usage=__ai_timetable__usage__,
    type="application",
    homepage="https://github.com/maoxig/nonebot-plugin-ai-timetable",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

table_help = on_command(
    "课表帮助", priority=20, block=False, aliases={"课表介绍", "课表怎么用"}
)

new_table = on_command("导入课表", priority=20, block=False, aliases={"创建课表"})
update_offline_table = on_command(
    "更新课表", priority=20, block=False, aliases={"更新本地课表"}
)
query_table = on_command(
    "课表查询", aliases={"查询课表","查询课程", "课程查询"}, priority=20, block=False
)


add_reminder = on_command("添加课程提醒", priority=20, block=False)
remove_reminder = on_command("删除课程提醒", priority=20, block=False)
query_reminder = on_command("查看课程提醒", priority=20, block=False)


@table_help.handle()
async def _(matcher: Matcher):
    """
    处理课表帮助命令，根据配置发送课表帮助信息或课表帮助图片
    """
    await send_table(matcher, __ai_timetable__usage__)


@new_table.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
):
    """
    处理导入课表命令，接收小爱课程表导出链接并更新本地课表
    """
    if args.extract_plain_text():
        matcher.set_arg("key", args)


@new_table.got(key="key", prompt="请发送小爱课程表导出的链接,发送/取消以退出")
async def _(event: Event, key: str = ArgPlainText()):
    """
    获取课表导出链接并更新本地课表
    """
    uid = event.get_user_id()
    logger.debug("获取的链接：" + key)
    await update_table(uid, key)
    await new_table.finish("导入成功")


@update_offline_table.handle(parameterless=[Depends(check_user)])
async def _(event: Event):
    uid = event.get_user_id()
    await update_offline_table_by_uid(uid)
    await update_offline_table.finish("更新成功")


@query_table.handle(parameterless=[Depends(check_user)])
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
):
    """
    处理查询课表命令，根据用户ID和关键词获取指定的课表并发送
    """
    if args.extract_plain_text():
        matcher.set_arg("key", args)


@query_table.got(key="key", prompt="查询什么课？")
async def _(event: Event, matcher: Matcher, key: str = ArgPlainText()):
    """
    处理查询课表命令，根据用户ID和关键词获取指定的课表并发送
    """
    uid = event.get_user_id()
    logger.debug("获取的参数：" + key)
    response = await build_table(uid, key)
    await send_table(matcher, response)


@add_reminder.handle(parameterless=[Depends(check_user), Depends(check_scheduler)])
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
):
    """
    处理添加提醒命令，解析用户输入的提醒内容并进行相应的处理
    """
    if args.extract_plain_text():
        matcher.set_arg("key", args)


@add_reminder.got(key="key", prompt="添加什么提醒？")
async def _(bot: Bot, matcher: Matcher, event: Event, key: str = ArgPlainText()):
    """
    获取用户输入的提醒内容并进行相应的处理
    """
    matcher.set_arg("key", key)
    logger.debug("提醒参数：" + key)
    uid = event.get_user_id()
    msg = await add_reminders(uid, key, bot, event)
    await add_reminder.finish(msg)


@remove_reminder.handle(parameterless=[Depends(check_user), Depends(check_scheduler)])
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
):
    """
    处理删除提醒命令，解析用户输入的提醒内容并进行相应的处理
    """
    if args.extract_plain_text():
        matcher.set_arg("key", args)


@remove_reminder.got(key="key", prompt="添加什么提醒？")
async def _(bot: Bot, matcher: Matcher, event: Event, key: str = ArgPlainText()):
    """
    获取用户输入的提醒内容并进行相应的处理
    """
    matcher.set_arg("text", key)
    logger.debug("提醒参数：" + key)
    uid = event.get_user_id()
    msg = await remove_reminders(uid, key)
    await remove_reminder.finish(msg)


@query_reminder.handle(parameterless=[Depends(check_user), Depends(check_scheduler)])
async def _(matcher: Matcher, event: Event):
    """
    处理查询提醒操作
    """
    uid = event.get_user_id()
    msg = await query_reminders_by_uid(uid)
    await send_table(matcher,msg)
