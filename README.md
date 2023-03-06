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

    ``` python
    暂无，以后可能慢慢增加
    ```

## 更新日志

- 2023-3-5:修复了无法取消订阅早八的bug
- 2023-3-6:新增了私聊订阅课表|早八的功能

## 命令

1. 我的课表|小爱课表|本周课表|下周课表：获取本周|下周的完全课表，使用前须先导入课表，这里的课表是在线课表

2. 导入课表：需要有小爱课表分享出来的链接，打开小爱课程表，手动添加课程或从教务导入(已适配了大部分高校)课程后

    ![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/get_thumbnail.jpg)

    在基本设置里把开始上课时间等调整好之后(尤其是时间、节数)，把分享课表得到的链接发送给bot即可导入本地
  
3. (昨天|今天|明天|后天|周X|星期x|)(课表|有啥课|上啥课)：查询指定天的课表，其中查询周x课表查询的是本周的

4. 订阅|取消订阅某天课表：导入本地课表后，发送订阅xx课表，如`订阅周一课表`，就可以在这天的前一天晚上10点定时推送第二天要上的课

5. 更新课表；如果在小爱课程表里修改了课程，发送该条指令即可更新本地的课表，无需重新导入

6. 订阅|取消订阅早八：会让bot在前一天晚上9点提醒你第二天是否有早八，以便决定今晚是否嗨皮（判定依据是是否存在第一节课）
  
7. 课表帮助：获取课表帮助

未完待续

## 计划

    ⬜︎ 完善插件
    
    ⬜︎ 增加更多的配置项

    ⬜︎ 查询下节课的信息

    ⬜︎ 订阅指定的课

    ⬜︎ 查询早八等

## 存在的问题

 1. 小爱课表分享的链接可能会过期，可能会导致无法进入指定页面截图(暂不清楚链接有效时间是多久)

 2. 机器人重启后定时任务会丢失

## 依赖

```python
nb plugin install nonebot_plugin_htmlrender
nb plugin install nonebot_plugin_apscheduler
```

若不安装nonebot_plugin_htmlrender插件会无法导入在线课表

## 喜欢的话就点个stars吧QAQ
