# 3 2 1 2 3

## discord機器人
名字:幽幽子
- 使用的語言
  - python
- 使用的庫
  - pycord - 主要指令運行庫
  - json - 數據資料儲存(次要)
  - yaml - 資料數據儲存(主要)
  - FileLock - 保護儲存數據文件
  - urllib.parse - 動態機器人邀請鏈接
  - dotenv - 變量環境token與discord user id 儲存
  - datetime - 獲取時間
  - discord.ui - ui系統(指令ui)
  - discord.ext - 指令
  - random - 隨機事件選取

## 指令？

通用指令 - 只限於普通用戶
> help - 獲取機器人全部指令
>
> ping - 獲取機器人與api之間的延遲
>
> roll - 簡單的丟骰子(有自定義參數可用)
>
> invite - 生成邀請機器人鏈接
>
> about-me - 關於我與機器人之間的訊息
>
> rpg_start - 目前已延期 有可能會廢置
>
> time - 可以獲取機器人待機多長時間(待機時間提供者"死亡協會")
>
> server_info - 可以獲取伺服器的資訊
>
> user_info - 可以獲取用戶的資訊
>
> feedback - 可以向我回報問題
>
> trivia - 開啓動漫的問答挑戰
>
> draw_lots - 抽籤(并非與日本傳説的御神籤)

管理員指令 - 只限於擁有管理員權限身份組
> ban - 封禁該用戶
>
> kick - 踢出該用戶
>
> timeout - 禁言該用戶
>
> untimeout - 解除禁言的用戶
>
> system_status - 可以查看機器人使用的資源情況
>
> clear - 清除訊息(不知道是什麽東西在搞到 還在修著)
>
> start_giveaway - 啓動一個抽獎活動

α作者使用的指令
> shutdown
>
> restart
>
> addmoney
>
> removemoney

minigame指令
> fish - 開啓釣魚的悠閑時光
>
> fish_shop - 開啓釣魚商店(數據提供者"釣魚協會")
>
> fish_back - 開啓你的漁獲背包(數據提供者"釣魚協會")
>
> fish_rod - 開啓並可以切換你的魚竿(數據提供者"釣魚協會")

剩餘指令敬請期待...

## 製作機器人的初衷
也許吧 可能就是爲了一些小群組吧 或者是爲了我自己

### 如何聯絡我
- Github
  - [xuemeng1987](https://github.com/xuemeng1987)
  - [Miya253](https://github.com/Miya253)
- Discord
  - [yuyuko bot test server](https://discord.gg/yGQQxvKHCn)
- X
  - [@yuemeng62](https://x.com/yuemeng200)
- Instagram
  - [Miya253](https://www.instagram.com/miya_2530_/)

## 未來預計計劃以及一些功能實現

### 1. Calendar Module / 日历模块
- **Description / 描述**: Implement a comprehensive calendar module that allows users to set up reminders for events.
  实现一个全面的日历模块，允许用户设置事件提醒。
- **Features / 功能**:
  - Customizable event scheduling (e.g., meetings, tasks).
    自定义事件安排（如会议、任务）。
  - Reminder notifications via Discord messages.
    通过Discord消息发送提醒通知。
  - Integration with existing functions (like economy or RPG events).
    与现有功能集成（如经济系统或RPG事件）。
- **Status / 状态**: Deprecated / 已廢棄。

### 2. Math Operation Expansion / 数学运算扩展
- **Description / 描述**: Enhance the calculator functionality with more operations and debugging.
  增强计算器功能，加入更多运算和调试。
- **Features / 功能**:
  - Basic and advanced operations (e.g., trigonometry, calculus).
    基础与高级运算（如三角函数、微积分）。
  - Improved error handling and input validation.
    改进错误处理与输入验证。
- **Status / 状态**: In progress (testing on test-main.py) / 进行中（测试中，文件：test-main.py）。

### 3. Language Support and Switching / 多语言支持与切换
- **Description / 描述**: Add multilingual support for the bot.
  为机器人添加多语言支持。
- **Features / 功能**:
  - A full-language.json file for handling translations.
    用full-language.json文件处理翻译。
  - Command `/language` to switch between supported languages.
    使用指令`/language`切换支持的语言。
- **Status / 状态**: Planned / 计划中。

### 4. Security and Automation / 安全与自动化
- **Description / 描述**: Improve bot security and add automation features.
  改进机器人的安全性并加入自动化功能。
- **Features / 功能**:
  - Website verification.
    网站验证。
  - Automatic moderation or message handling.
    自动管理或消息处理。
- **Status / 状态**: Deprecated / 已廢棄。

### 5. Economy System Leaderboard and Stats Display / 经济系统排行榜和统计显示
- **Description / 描述**: Introduce a leaderboard for economy-based interactions and stats display.
  引入经济系统互动的排行榜及统计数据显示。
- **Features / 功能**:
  - Display top earners and transaction history.
    显示最高收入者和交易记录。
  - Detailed user statistics (work, balance, etc.).
    用户详细统计（工作、余额等）。
- **Status / 状态**: accomplish / 已完成

### 6. RPG Mini-Game Debugging / RPG小游戏调试
- **Description / 描述**: Continue debugging and improving the RPG mini-game for entertainment purposes.
  继续调试和改进RPG小游戏，提升娱乐性。
- **Features / 功能**:
  - Combat system enhancements.
    战斗系统增强。
  - Item, skill, and progression mechanics.
    道具、技能与进度机制。
- **Status / 状态**: In progress (debugging) / 进行中（调试中）。

### 7. Automation: Moving Towards Auto Bot / 自动化：向自动机器人发展
- **Description / 描述**: Gradually shift more features towards automated operations.
  逐步将更多功能转向自动化操作。
- **Features / 功能**:
  - Automatic reminders, message handling, economy activities.
    自动提醒、消息处理、经济活动等功能。
  - Tag the bot as "Auto Bot."
    将机器人标记为“自动机器人”。
- **Status / 状态**: Long-term goal / 长期目标。

## 一些對抄襲仔的警告

### **禁止抄袭声明 Anti-Plagiarism Notice**
任何未经授权的代码抄袭、盗用或使用此开源代码的行为都将面临法律行动。

### 任何未经授权的代码抄袭盗用 或使用此开源代码的行为都将面临法律行动
- 行動方式如下
  - [第36條](http://www.commonlii.org/my/legis/consol_act/ca1987133/s36.html)
  - [第42條](https://www.myipo.gov.my/ms/copyright-act-1987/)
