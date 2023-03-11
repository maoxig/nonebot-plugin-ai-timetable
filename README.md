<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot-plugin-ai-timetable

✨*基于Nonebot2的对接小爱课程表的插件*✨
  
<div align="left">
  
# 前言

   这是本人第一次在github发布的项目，也是第一个python项目，完全是萌新，很多地方写的可能很拉，大佬轻喷
目前还不是很完善，有什么bug或者建议欢迎提issues

## 安装

1. 通过`pip`或`nb`安装；

2. 本地数据保存在`/data/ai_timetable/userdata.json`以及`/data/ai_timetable/usertable.json`，分别对应用户发送的链接和本地保存的课表

## 简介

1. 傻瓜式一键导入小爱课表，让你的bot实现小爱课表的功能

2. 用户课表数据隔离，无需担心课程时间冲突、不同学校课表不同等问题

3. ~~所以为什么不直接用小爱课表呢~~

4. 插件配置

如果想要修改配置，在机器人目录下的.env.*里面可以填写以下选项(可选)

| config                  | type  | default |          example           | usage                                               |
| :---------------------- | :---: | :-----: | :------------------------: | :-------------------------------------------------- |
| TIMETABLE_PIC           | bool  |  true   |    TIMETABLE_PIC=false     | 可选择某日课表以图片/文字发送，默认以图片发送(true) |
| TIMETABLE_ALOCK_SOMEDAY |  int  |   22    | TIMETABLE_ALOCK_SOMEDAY=15 | 订阅某日课表的发送时间，必须是0-24的数字            |
| TIMETABLE_ALOCK_8       |  int  |   21    | TIMETABLE_ALOCK_SOMEDAY=16 | 订阅早八的发送时间，必须是0-24的数字                |

## 依赖

```python
nb plugin install nonebot_plugin_htmlrender
nb plugin install nonebot_plugin_apscheduler
```

若不安装nonebot_plugin_htmlrender插件会无法导入在线课表

不安装nonebot_plugin_apscheduler会无法使用定时任务,其他功能无影响

## 更新日志

<details>
<summary>点击展开</summary>

- 2023-03-05:

    修复了无法取消订阅早八的bug

- 2023-03-06:
  
    新增了私聊订阅课表|早八的功能

- 2023-03-07:

1. 修复了时间不会自己改变的bug
2. 新增了上课/下节课 功能
3. 优化了一些屎山代码

- 2023-03-08:

1. 修改部分代码，优化课表格式

2. 修复了节数为11的课会排在节数为2的课程前面的bug(QAQ太蠢了别骂了别骂了)

- 2023-03-11:

1. 修复了如果未登录小米账户就分享课表时的报错,增加错误提示
2. 新增3项配置项，某日课表可选择以图片发送（默认为图片）

</details>

## 命令

1. 我的课表|小爱课表|本周课表|下周课表：获取本周|下周的完全课表，使用前须先导入课表，这里的课表是在线课表

2. 导入课表：需要有小爱课表分享出来的链接，打开小爱课程表，手动添加课程或从教务导入(已适配了大部分高校)课程后

    ![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/export.jpg)

    在基本设置里把开始上课时间等调整好之后(尤其是时间、节数)，把分享课表得到的链接发送给bot即可导入本地(分享前需要登录小米账户 #1)
  
3. (昨天|今天|明天|后天|周X|星期x|)(课表|有啥课|上啥课)：查询指定天的课表，其中查询周x课表查询的是本周的

4. 订阅|取消订阅某天课表：导入本地课表后，发送订阅xx课表，如`订阅周一课表`，就可以在这天的前一天晚上10点定时推送第二天要上的课

5. 更新课表；如果在小爱课程表里修改了课程，发送该条指令即可更新本地的课表，无需重新导入

6. 订阅|取消订阅早八：会让bot在前一天晚上9点提醒你第二天是否有早八，以便决定今晚是否嗨皮（判定依据是是否存在第一节课）

7. 上课|下节课：获取当前上课信息，返回下节课信息(如果有)

8. 课表帮助：获取课表帮助

未完待续

## 效果图

![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/my_table.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/alock_8.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/next_class.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/someday_classes.jpg)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/someday_classes_pic.jpg)
### 关于小爱课程表内的一些说明

如下图

- 首先要登录上小米账户,否则可能获取到错误的课表信息 #1
- 设置好开始上课时间
- 设置好课程时间，可以修改每节课具体的时间，
- 课表节数按自己需求调，一般教务导入的课表节数可能不符合实际，需要微调
- 每周起始日建议默认的周一即可（周日起始没测试过可能有bug）
- 如果导入课表后在小爱课表内修改了课程，直接给bot发送更新课表即可更新本地课表
- 当你主页的课表和学校课表基本一致时，那么小爱课程表就被调教好了，可以导入了

![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/settings.jpg)

## 计划

- [x] 查询下节课的信息

- [x] 可选择是否发送图片以避免风控

- [x] 增加更多的配置项

- [ ] 完善插件

- [ ] 订阅指定的课

- [ ] 查询早八

## 存在的问题

 1. 小爱课表分享的链接可能会过期，可能会导致无法进入指定页面截图(暂不清楚链接有效时间是多久)

 2. 机器人重启后定时任务会丢失

## 喜欢的话就点个star吧QAQ
