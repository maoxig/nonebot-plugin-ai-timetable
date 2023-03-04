<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot-plugin-ai-timetable

 ✨*基于Nonebot2的对接小爱课表的插件*✨



# 前言

   这是本人第一次在github发布的项目，也是第一个python项目，完全是萌新，很多地方写的可能很拉，大佬轻喷
目前还不是很完善，有什么bug或者建议欢迎提issue

## 安装

1. 通过`pip`或`nb`安装；

2. 本地数据保存在`/data/userdata.json`以及`/data/usertable`，分别对应用户发送的链接和本地保存的课表

## 简介

1. 一键导入小爱课表，让你的bot实现小爱课表的功能

2. 插件配置

    ``` python
    暂无，以后可能慢慢增加
    ```


## 命令

1. 我的课表、小爱课表、本周课表、下周课表：获取本周/下周的完全课表，使用前须先导入课表

2. 导入课表：先打开小爱课程表，手动添加或从教务导入课程后

    ![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/get_thumbnail.jpg)

    在基本设置里把开始上课时间等调整好之后，把分享课表得到的链接发送给bot即可导入

3. 订阅/取消订阅某天课表：导入课表后，发送订阅xx课表，如`订阅周一课表`，就可以在这天的前一天晚上10点定时推送第二天要上的课

4. 更新课表；如果在小爱课程表里修改了课程，发送该条指令即可更新本地的课表

未完待续

 ## 计划
 
    ⬜︎ 完善插件
    
    ⬜︎ 增加更多的配置项

    ⬜︎ 查询下节课的信息

    ⬜︎ 订阅指定的课

    ⬜︎ 查询早八等
   
## 存在的问题
 1. 小爱课表分享的链接可能会过期，可能会导致无法进入指定页面截图
 2. 还不能做到私聊订阅课表
 3. 机器人重启后定时任务会丢失


## 依赖

```python
nb plugin install nonebot_plugin_htmlrender
nb plugin install nonebot_plugin_apscheduler
```

若不安装nonebot_plugin_htmlrender插件会无法导入在线课表
