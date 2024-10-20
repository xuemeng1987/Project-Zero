# Discord Bot

欢迎使用我们的 Discord 机器人！此机器人旨在通过多种功能和指令增强您的服务器体验。以下是现有指令和功能的概览。

Welcome to our Discord bot! This bot is designed to enhance your server with various functionalities and commands. Below is an overview of the available commands and features.

## **功能 Features**

### **通用指令 General Commands**
- **`/invite`**: 生成机器人的邀请链接。 / Generates an invite link for the bot.
- **`/ping`**: 显示机器人的当前延迟。 / Shows the bot's current latency.
- **`/time`**: 显示机器人的最后活动时间。 / Displays the bot's last activity time.
- **`/trivia`**: 启动一个动漫问答挑战。 / Start a Trivia Quiz Challenge (Anime).

### **经济系统 Economy System**
- **`/balance`**: 查看您的幽灵币余额。 / Check your Ghost Coin balance.
- **`/work`**: 通过工作赚取幽灵币。 / Earn Ghost Coin by working.
- **`/pay`**: 向其他用户转账幽灵币。 / Transfer Ghost Coin to another user.
- **`/addmoney`**: 向用户账户添加幽灵币（仅限管理员）。 / Add Ghost Coin to a user’s account (admin only).
- **`/removemoney`**: 从用户账户移除幽灵币（仅限管理员）。 / Remove Ghost Coin from a user’s account (admin only).

### **管理员指令 Admin Commands**
- **`/ban`**: 禁止用户进入服务器（仅限管理员）。 / Bans a user from the server (admin only).
- **`/kick`**: 踢出服务器用户（仅限管理员）。 / Kicks a user from the server (admin only).
- **`/clear`**: 清理频道中的消息（仅限管理员）。 / Clears messages from the channel (admin only).
- **`/start_giveaway`**: 开始一个抽奖活动（仅限管理员）。 / Start a giveaway event (Admins only).

### **用户和服务器信息 User and Server Info**
- **`/server_info`**: 提供服务器信息。 / Provides information about the server.
- **`/user_info`**: 提供用户信息。 / Provides information about a user.

### **反馈 Feedback**
- **`/feedback`**: 报告机器人的错误或问题。 / Report a bug or issue with the bot.

## **即将推出的功能 Upcoming Features**
*注意：RPG 地下城冒险功能仍在开发中，敬请期待。*
*Note: The RPG Dungeon Adventure feature is still in development and will be available soon.*

## **安装 Installation**

1. 克隆仓库：/ Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   ```
2. 进入项目目录：/ Navigate to the project directory:
   ```bash
   cd your-repo-name
   ```
3. 安装所需依赖：/ Install the required dependencies:
   ```bash
   pip install
   ```
4. 在根目录下创建一个 .env 文件并添加你的机器人 token：/ Create a .env file in the root directory and add your bot token:
   ```env
   BOT_TOKEN=your-bot-token-here
   ```
5. 运行机器人：/ Run the bot:
   ```bash
   python bot.py
   ```

## **注意 Note**
部分代码中涉及机器人关闭时的硬编码 **`AUTHOR_ID`**，可以在 **`.env`** 文件中设置您的实际 **`Discord ID`**。示例如下：

In some parts where the bot is shut down, there is a hardcoded **`AUTHOR_ID`**. You can set your actual **`Discord ID`** in the **`.env`** file. The setup would look like this:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
AUTHOR_ID=your_discord_id
```
### **贡献 Contributing**
欢迎任何贡献！请 fork 此仓库并创建 pull request 来提交您的更改。如果是重大更改，请先打开一个 issue 以讨论您想要更改的内容。

Feel free to contribute to this project! Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## **邀请机器人 Invite The Bot**
[yuyukobot](https://discord.com/oauth2/authorize?client_id=852046004550238258&permissions=15&scope=bot)

## **联系 Contact**
如果您有任何问题或需要帮助，可以通过以下方式联系我：

If you have any questions or need assistance, you can contact me through:

- Discord: Miya253
- X: [@yuemeng62](https://x.com/yuemeng200)
- GitHub: [xuemeng1987](https://github.com/xuemeng1987)

## **禁止抄袭声明 Anti-Plagiarism Notice**
任何未经授权的代码抄袭、盗用或使用此开源代码的行为都将面临法律行动。

Any unauthorized plagiarism, misappropriation, or misuse of this open-source code will result in legal action.
