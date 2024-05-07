<div align="center">
  <a href="https://nonebot.dev/">
    <img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-ai-timetable

✨ *基于Nonebot2的对接小爱课程表的插件* ✨


  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot-v2-red" alt="nonebot">
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/maoxig/nonebot-plugin-ai-timetable" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-ai-timetable">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ai-timetable" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</div>

## 💿安装

1. 通过`pip`或`nb`安装；
    - 使用nb(推荐)
  
       在机器人目录下命令行使用`nb plugin install nonebot_plugin_ai_timetable`

    - 使用pip:
  
      `pip plugin install nonebot_plugin_ai_timetable`

      然后在机器人`pyproject.toml`里的`plugins = []`列表追加`"nonebot_plugin_ai_timetable"`

    - 使用其他包管理器：

      根据包管理器的指令安装插件

2. 数据存储使用[plugin-orm](https://github.com/nonebot/plugin-orm), 使用`nb orm upgrade`升级数据库

> [!WARNING]
> 第一次使用[plugin-orm](https://github.com/nonebot/plugin-orm)，或者插件定义的模型有所更新时，需要用`nb orm upgrade`升级数据库

## 📖简介

1. 傻瓜式一键导入小爱课表，让你的bot实现小爱课表的功能

2. 用户课表数据隔离，基于[plugin-rom](https://github.com/nonebot/plugin-orm), 接入数据库，无需担心课程时间冲突、不同学校课表不同等问题

3. 适配多平台，即使是电报涩涩群也要好好学习！🥵🥵

## ⚙️插件配置

>[!NOTE] 可选的插件配置
这些配置都已设好默认值，因此是可选的，如果想要修改配置，在机器人目录下的.env.*里面可以填写以下选项, 未来会考虑开放更多的配置项

|         config          | type  | default |          example           | usage                                                                                                 |
| :---------------------: | :---: | :-----: | :------------------------: | :---------------------------------------------------------------------------------------------------- |
|      TIMETABLE_PIC      | bool  |  true   |    TIMETABLE_PIC=false     | 可选择某日课表以图片/文字发送，默认以图片发送(true)                                                   |
| TIMETABLE_ALOCK_SOMEDAY |  int  |   22    | TIMETABLE_ALOCK_SOMEDAY=15 | 订阅某日课表的发送时间，必须是0-24的数字                                                              |
|    TIMETABLE_ALOCK_8    |  int  |   21    |    TIMETABLE_ALOCK_8=16    | 订阅早八的发送时间，必须是0-24的数字.这里发送的都是第二天的，所以建议设置为18-23点                    |
|   TIMETABLE_SEND_TIME   | float |   0.5   |   TIMETABLE_SEND_TIME=1    | 订阅课程提前发送的时间，单位是`小时`，可以是整数也可以是小数，建议不要设的太大，避免出现无法预料的bug |


## 💿依赖

> [!NOTE]
> 插件依赖会在安装时自动安装，如果安装失败，你可以按照以下指令手动再次安装

```python
nb plugin install nonebot_plugin_htmlrender
nb plugin install nonebot_plugin_apscheduler
nb plugin install nonebot_plugin_alconna
nb plugin install nonebot_plugin_orm
```

## 🌙更新日志

<details>
<summary>点击展开</summary>

- 0.4.1 / 2024-05-07:
   1. 修复定时提醒一直发送的问题
   2. 更新README.md
   3. 修复type hint错误

- 0.4.0 / 2024-04-30:
   1. 重构完成，将所有数据迁移到官方数据库插件[plugin-orm](https://github.com/nonebot/plugin-orm)，之前的数据失效
   2. 修改了插件触发指令和相关逻辑
   3. 重构所有代码，优化处理逻辑
   >该版本是破坏性更新，且仍在测试中，有任何疑问欢迎issue或pr

- 0.3.8 / 2024-04-28:
   1. 修复设置错误
   2. 重构代码

- 0.3.7 / 2024-04-24:
   1. 更新Nonebot2版本至2.2.0
   2. 基于 [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 适配多平台
   3. 放宽httpx限制，移除onebot依赖

- 0.3.6 / 2023-09-02:
   1. 适配nonebot2.0.1版本：移除过时的RegexMatch方法
   >如更新本插件后接受消息无响应，请更新你的nonebot版本或回退到旧版本使用

- 0.3.5 / 2023-08-10:
   1. 格式化代码
   2. 优化配置读取
   3. 更新插件元数据

- 0.3.5 / 2023-06-09:
   1. 更新httpx依赖版本

- 0.3.3 / 2023-04-23:
   1. 修复定时提醒重复发送的bug
   2. 修改帮助

- 0.3.2 / 2023-04-14:
   1. 删去了文本中所有奇怪的口癖喵
   2. 修复了订阅课程发送时间错误的bug

- 0.3.0 / 2023-04-02:
   1. 修复bug
   2. 优化帮助图片
   3. 定时任务随机延后0-60s，防止风控
   4. 增加订阅指定课程的功能

- 0.2.3 / 2023-03-29:
   1. 重构了代码，优化了许多地方~~真的累死了~~
   2. 修复了一些bug，优化了体验
   3. 增加了早八|明日早八的查询
   4. 更新版本后建议重新`导入课表`，避免出现某些bug

- 0.2.1 / 2023-03-13:
   1. 修复订阅早八的一些bug

- 0.2.0 / 2023-03-11:
   1. 修复了如果未登录小米账户就分享课表时的报错，增加错误提示
   2. 新增3项配置项，某日课表可选择以图片发送（默认为图片）

- 0.1.8 / 2023-03-08:
   1. 修改部分代码，优化课表格式
   2. 修复了节数为11的课会排在节数为2的课程前面的bug(QAQ太蠢了别骂了别骂了)

- 0.1.7 / 2023-03-07:
   1. 修复了时间不会自己改变的bug
   2. 新增了上课/下节课功能
   3. 优化了一些屎山代码

- 0.1.5 / 2023-03-06:
   1. 新增了私聊订阅课表|早八的功能

- 0.1.4 / 2023-03-05:
   1. 修复了无法取消订阅早八的bug

</details>

## 🎉命令

- 课表帮助：获取本条帮助

- 导入课表：需要有小爱课表分享出来的链接，打开小爱课程表，手动添加课程或从教务导入(已适配了大部分高校)课程后

    ![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/export.jpg)

    在基本设置里把开始上课时间等调整好之后(尤其是时间、节数)，把分享课表得到的链接发送给bot即可导入本地

> [!NOTE]
> 在分享前，你需要登录小米账户 [#1](https://github.com/maoxig/nonebot-plugin-ai-timetable/issues/1)

- 更新课表；如果在小爱课程表里修改了课程，发送该条指令即可更新本地的课表，无需重新导入
  
- 查询课表+[参数]：查询[参数]的课表，参数支持[本周/下周、周x、昨天/今天/明天/后天、早八、课程名、下节课]

- 添加课程提醒+[参数]：参数支持[周x、早八、课程名]

- 删除课程提醒+[参数]：参数支持[全部、周x、早八、课程名]

- 查看课程提醒：查看当前已经添加的课程提醒

## ⭐效果图

![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/update.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/query.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/query1.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/query1.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/reminder.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/reminder1.png)
![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/someday_classes_pic.jpg)

### 😥我不知道怎么使用小爱课程表

如下图

- 首先要登录上小米账户,否则可能获取到错误的课表信息 [#1](https://github.com/maoxig/nonebot-plugin-ai-timetable/issues/1)
- 设置好开始上课时间
- 设置好课程时间，可以修改每节课具体的时间，
- 课表节数按自己需求调，一般教务导入的课表节数可能不符合实际，需要微调
- 每周起始日建议默认的周一即可
- 如果导入课表后在小爱课表内修改了课程，直接给bot发送更新课表即可更新本地课表
- 当你主页的课表和学校课表基本一致时，那么小爱课程表就被设置好了，可以导入了

![Image text](https://github.com/maoxig/nonebot-plugin-ai-timetable/blob/main/resource/settings.jpg)

## 🐦计划

- [x] 查询下节课的信息

- [x] 可选择是否发送图片以避免风控

- [x] 增加更多的配置项

- [x] 重构代码

- [x] 订阅指定的课

- [x] 多平台适配, 基于 [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 

- [x] 支持定时任务本地存储

- [x] 适配[plugin-orm](https://github.com/nonebot/plugin-orm), 接入数据库

- [ ] 适配更多课表、脱离小爱课表

- [ ] 完善插件

## 🐛存在的问题

> [!NOTE]
> 在当前版本下，Bot重启后会失去之前创建过的任务，这个问题暂时无法解决

众所周知，使用apscheduler添加的定时任务，会在bot重启后丢失，这是因为使用[nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler)创建出来的`scheduler`，默认使用的`JobStore`(即保存任务的方式)，是`MemoryJobStore`，也就是存在内存中，因此会导致重启丢任务。

因此参考[apscheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html#configuring-the-scheduler)，你可以在bot的配置文件中添加配置项，让[nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler)创建出来的`scheduler`的默认 `JobStore` 改为使用数据库，这样就可以持久化存储任务，而不需要额外修改任何东西。

然而，很不幸的是，在`apscheduler4.0`版本之前，所支持的数据库类JobStore都是使用**同步**引擎的，不支持异步引擎，然而[plugin-orm](https://github.com/nonebot/plugin-orm)所采用的是异步引擎，因此你暂时还不能这样做。

所以，暂时还无法解决定时任务的持久化存储问题，除非`apscheduler`正式发版4.0（目前还是alpha版本），你可以再等待，本插件会持续跟进更新。

## 🎉致谢

- 感谢[nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender)提供的渲染工具
- 感谢[plugin-orm](https://github.com/nonebot/plugin-orm)提供的异步数据库接口
- 感谢[nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler)提供的定时任务接口
- 感谢[nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna)
- 感谢[Matcha](https://github.com/A-kirami/matcha)提供的简单好用的测试平台

### ✨喜欢的话就点个star吧

或者, 你也可以看我写的其他插件
[nonebot-plugin-manga-translator](https://github.com/maoxig/nonebot-plugin-manga-translator)一个支持多api（包括离线部署）、跨平台、方便好用的图片/漫画翻译插件
