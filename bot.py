import discord
import subprocess
import time
import asyncio
import discord.state
import json
import random
import os
import sys
import logging
import aiohttp
import aiofiles
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from urllib.parse import urlparse
from responses import food_responses, death_responses, life_death_responses, self_responses, friend_responses, maid_responses, mistress_responses, reimu_responses, get_random_response

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN_MAIN_BOT')
AUTHOR_ID = int(os.getenv('AUTHOR_ID'))
LOG_FILE_PATH = "feedback_log.txt"

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.message_content = True
last_activity_time = time.time()
intents.messages = True
participants = []

class URLBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.whitelist = set()
        self.load_whitelist()

    def load_whitelist(self):
        try:
            with open('whitelist.json', 'r') as file:
                self.whitelist = set(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            self.whitelist = set()

    async def save_whitelist(self):
        async with aiofiles.open('whitelist.json', 'w') as file:
            await file.write(json.dumps(list(self.whitelist)))

    def is_domain_whitelisted(self, domain):
        return any(domain.endswith(whitelisted) for whitelisted in self.whitelist)

bot = URLBot(command_prefix='/', intents=intents)

user_balance = {}

def save_balance(data):
    with open('balance.json', 'w') as f:
        json.dump(data, f)

def load_balance():
    if os.path.exists('balance.json'):
        with open('balance.json', 'r') as f:
            return json.load(f)
    return {}

user_balance = load_balance()

def load_dm_messages():
    try:
        with open('dm_messages.txt', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_dm_messages(dm_messages):
    with open('dm_messages.txt', 'w') as file:
        json.dump(dm_messages, file, indent=4)

dm_messages = load_dm_messages()

def load_trivia_questions():
    with open('trivia_questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['questions']

questions = load_trivia_questions()

def get_random_question():
    return random.choice(questions)

def load_whitelist():
    try:
        with open('whitelist.json', 'r') as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_whitelist():
    with open('whitelist.json', 'w') as file:
        json.dump(list(whitelist), file)

whitelist = load_whitelist()

def load_deleted_messages():
    try:
        with open('deleted_messages.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_deleted_message(message_data):
    deleted_messages = load_deleted_messages()
    deleted_messages.append(message_data)
    with open('deleted_messages.json', 'w') as file:
        json.dump(deleted_messages, file, indent=4)

async def check_url_safety(url: str) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                content = await response.text()
                if "adult" in content.lower() or "unsafe" in content.lower():
                    return False
        except Exception as e:
            logging.warning(f"Failed to check URL {url}: {e}")
            return False
    return True

@bot.event
async def on_message(message):
    global last_activity_time
    
    if message.author == bot.user:
        return
    
    if message.webhook_id:
        return
    
    content = message.content
    
    if '關於機器人幽幽子' in message.content.lower():
        await message.channel.send('幽幽子的創建時間是<t:1623245700:D>')
    
    if '關於製作者' in message.content.lower():
        await message.channel.send('製作者是個很好的人 雖然看上有有點怪怪的')
    
    if '幽幽子的生日' in message.content.lower():
        await message.channel.send('機器人幽幽子的生日在<t:1623245700:D>')

    if '熊貓' in message.content.lower():
        await message.channel.send('Miya253:幹嘛 我現在在修著幽幽子 有事情的話請DM我 謝謝')
    
    if message.content.startswith('關閉幽幽子'):
        if message.author.id == AUTHOR_ID:
            await message.channel.send("正在關閉...")
            await asyncio.sleep(5)
            await bot.close()
            return
        else:
            await message.channel.send("你無權關閉我 >_< ")
            return

    elif message.content.startswith('重啓幽幽子'):
        if message.author.id == AUTHOR_ID:
            await message.channel.send("正在重啟幽幽子...")
            subprocess.Popen([sys.executable, os.path.abspath(__file__)])
            await bot.close()
            return
        else:
            await message.channel.send("你無權重啓我 >_< ")
            return

    if '幽幽子待機多久了' in message.content.lower():
        current_time = time.time()
        idle_seconds = current_time - last_activity_time
        idle_minutes = idle_seconds / 60
        await message.channel.send(f'幽幽子目前已待機了 **{idle_minutes:.2f} 分钟**')

    if isinstance(message.channel, discord.DMChannel):
        user_id = str(message.author.id)
        if user_id not in dm_messages:
            dm_messages[user_id] = []
        dm_messages[user_id].append({
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        })
        save_dm_messages(dm_messages)
        print(f"Message from {message.author}: {message.content}")
    
    if 'これが最後の一撃だ！名に恥じぬ、ザ・ワールド、時よ止まれ！' in message.content.lower():
        await message.channel.send('ザ・ワールド\nhttps://tenor.com/view/the-world-gif-18508433')

        await asyncio.sleep(1)
        await message.channel.send('一秒経過だ！')

        await asyncio.sleep(3)
        await message.channel.send('二秒経過だ、三秒経過だ！')

        await asyncio.sleep(4)
        await message.channel.send('四秒経過だ！')

        await asyncio.sleep(5)
        await message.channel.send('五秒経過だ！')

        await asyncio.sleep(6)
        await message.channel.send('六秒経過だ！')

        await asyncio.sleep(7)
        await message.channel.send('七秒経過した！')

        await asyncio.sleep(8)
        await message.channel.send('ジョジョよ、**私のローラー**!\nhttps://tenor.com/view/dio-roada-rolla-da-dio-brando-dio-dio-jojo-dio-part3-gif-16062047')
    
        await asyncio.sleep(9)
        await message.channel.send('遅い！逃げられないぞ！\nhttps://tenor.com/view/dio-jojo-gif-13742432')
    
    if '星爆氣流斬' in message.content.lower():
        await message.channel.send('アスナ！クライン！')
        await message.channel.send('**頼む、十秒だけ持ち堪えてくれ！**')
        
        await asyncio.sleep(2)
        await message.channel.send('スイッチ！')
    
        await asyncio.sleep(10)
        await message.channel.send('# スターバースト　ストリーム！')
        
        await asyncio.sleep(5)
        await message.channel.send('**速く…もっと速く！！**')
        
        await asyncio.sleep(15)
        await message.channel.send('終わった…のか？')        
        
    if '食物' in content:
        await message.channel.send(get_random_response(food_responses))

    elif '死亡' in content:
        await message.channel.send(get_random_response(death_responses))

    elif '生死' in content:
        await message.channel.send(get_random_response(life_death_responses))
    
    elif '關於幽幽子' in content:
        await message.channel.send(get_random_response(self_responses))
    
    elif '關於幽幽子的朋友' in content:
        await message.channel.send(get_random_response(friend_responses))
    
    elif '關於紅魔館的女僕' in content:
        await message.channel.send(get_random_response(maid_responses))
    
    elif '關於紅魔舘的大小姐和二小姐' in content:
        await message.channel.send(get_random_response(mistress_responses))
    
    elif '關於神社的巫女' in content:
        await message.channel.send(get_random_response(reimu_responses))

    if message.embeds:
        for embed in message.embeds:
            if embed.url is not None and (embed.type == 'gifv' or 'gif' in embed.url):
                domain = urlparse(embed.url).netloc
                if not bot.is_domain_whitelisted(domain):
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, 該GIF來自未经许可的域名，不允许发送。")
                    return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.url.endswith(('gif', 'gifv')):
                domain = urlparse(attachment.url).netloc
                if not bot.is_domain_whitelisted(domain):
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, 該附件 GIF 不在白名单中，不允许发送。")
                    return

    urls = [word for word in message.content.split() if word.startswith('http')]
    for url in urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        if not bot.is_domain_whitelisted(domain):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, 此链接不在白名单中。")
            return
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'已登入 {bot.user.name}')
    
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.playing, name='Honkai: Star Rail')
    )
    
    try:
        synced = await bot.tree.sync()
        print(f'成功同步 {len(synced)} 个命令')
    except Exception as e:
        print(f'同步命令时出错: {e}')
    
    last_activity_time = time.time()

@bot.tree.command(name="invite", description="生成机器人的邀请链接")
async def invite(interaction: discord.Interaction):
    client_id = bot.user.id
    permissions = 15
    invite_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"
    
    await interaction.response.send_message(f"邀请链接：{invite_url}")

@bot.tree.command(name="rpg_start", description="初始化RPG數據")
async def rpg(interaction: discord.Interaction):
    message = "RPG系統正在製作中 預計時裝時間是 <t:1727712000:R>"
    await interaction.response.send_message(message)

@bot.tree.command(name="balance", description="查询用户余额")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = user_balance.get(user_id, 0)
    await interaction.response.send_message(f'{interaction.user.name} 的比特幣余额: {balance}')

@bot.tree.command(name="work", description="赚取比特幣")
async def work(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    amount = random.randint(10, 1000)
    user_balance[user_id] = user_balance.get(user_id, 0) + amount
    save_balance(user_balance)
    await interaction.response.send_message(f'{interaction.user.name} 赚取了 {amount} 比特幣！')

@bot.tree.command(name="pay", description="转账给其他用户")
async def pay(interaction: discord.Interaction, member: discord.Member, amount: int):
    user_id = str(interaction.user.id)
    recipient_id = str(member.id)
    if user_id == recipient_id:
        await interaction.response.send_message("不能转账给自己")
        return
    if user_balance.get(user_id, 0) < amount:
        await interaction.response.send_message("余额不足")
        return
    user_balance[user_id] -= amount
    user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
    save_balance(user_balance)
    await interaction.response.send_message(f'{interaction.user.name} 给 {member.name} 转账了 {amount} 比特幣')

@bot.tree.command(name="addmoney", description="给用户增加比特币（管理员专用）")
async def addmoney(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.guild_permissions.administrator:
        recipient_id = str(member.id)
        user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
        save_balance(user_balance)
        await interaction.response.send_message(f'给 {member.name} 增加了 {amount} 比特币。')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="removemoney", description="移除用户比特币（管理员专用）")
async def removemoney(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.guild_permissions.administrator:
        recipient_id = str(member.id)
        if recipient_id in user_balance:
            user_balance[recipient_id] = max(user_balance[recipient_id] - amount, 0)
            save_balance(user_balance)
            await interaction.response.send_message(f'从 {member.name} 移除了 {amount} 比特币。')
        else:
            await interaction.response.send_message(f'{member.name} 没有比特币记录。')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="shutdown", description="关闭机器人")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == AUTHOR_ID:
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("关闭中...")
            await bot.close()
        except Exception as e:
            print(f"Shutdown command failed: {e}")
    else:
        await interaction.response.send_message("你没有权限执行此操作。", ephemeral=True)

@bot.tree.command(name="restart", description="重启机器人")
async def restart(interaction: discord.Interaction):
    if interaction.user.id == AUTHOR_ID:
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("重启中...")
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            print(f"Restart command failed: {e}")
    else:
        await interaction.response.send_message("你没有权限执行此操作。", ephemeral=True)

@bot.tree.command(name="ban", description="封禁用户")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("你没有权限执行此操作。")
        return
    
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("我没有权限执行此操作。")
        return

    if interaction.guild.me.top_role <= member.top_role:
        await interaction.response.send_message("我无法封禁此用户，因我的角色权限不足。")
        return
    
    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member} 已被封禁.')

@bot.tree.command(name="kick", description="踢出用户")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("你没有管理员权限，无法执行此操作。")
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member} 已被踢出。')

@bot.tree.command(name="clear", description="清除消息")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer()

    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("你没有管理员权限，无法执行此操作。")
        return

    if amount <= 0:
        await interaction.followup.send("请输入一个大于 0 的数字。")
        return
    if amount > 100:
        await interaction.followup.send("无法一次性删除超过 100 条消息。")
        return

    cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=30)
    deleted = 0

    async for message in interaction.channel.history(limit=amount):
        if message.created_at >= cutoff_date:
            await message.delete()
            deleted += 1
            await asyncio.sleep(5)

    await interaction.followup.send(f'已删除 {deleted} 条消息。')

@bot.tree.command(name="time", description="获取最后活动时间")
async def time_command(interaction: discord.Interaction):
    global last_activity_time
    current_time = time.time()
    idle_seconds = current_time - last_activity_time
    idle_minutes = idle_seconds / 60
    await interaction.response.send_message(f'机器人上次活动时间是 {idle_minutes:.2f} 分钟前。')

@bot.tree.command(name="ping", description="显示机器人的延迟")
async def ping(interaction: discord.Interaction):
    latency = bot.latency * 1000
    await interaction.response.send_message(f'当前延迟为 {latency:.2f} 毫秒')

@bot.tree.command(name='add_whitelist', description='將URL加入白名單')
async def add_whitelist(interaction: discord.Interaction, url: str):
    if interaction.user.guild_permissions.administrator:
        bot.whitelist.add(url)
        await bot.save_whitelist()
        await interaction.response.send_message(f"{url} 已加入白名單。")
    else:
        await interaction.response.send_message("你沒有權限執行此指令。")

@bot.tree.command(name='remove_whitelist', description='將URL從白名單移除')
async def remove_whitelist(interaction: discord.Interaction, url: str):
    if interaction.user.guild_permissions.administrator:
        if url in bot.whitelist:
            bot.whitelist.remove(url)
            await bot.save_whitelist()
            await interaction.response.send_message(f"{url} 已從白名單移除。")
        else:
            await interaction.response.send_message(f"{url} 不在白名單中。")
    else:
        await interaction.response.send_message("你沒有權限執行此指令。")

@bot.tree.command(name='show_whitelist', description='顯示白名單')
async def show_whitelist(interaction: discord.Interaction):
    if bot.whitelist:
        await interaction.response.send_message("\n".join(bot.whitelist))
    else:
        await interaction.response.send_message("白名單是空的。")

@bot.tree.command(name="roll", description="擲骰子")
async def roll(interaction: discord.Interaction, max_value: int = None):
    """擲骰子指令，預設最大值為100，用戶可以指定最大值"""
    if max_value is None:
        max_value = 100
    
    if max_value < 1:
        await interaction.response.send_message("請輸入一個大於0的數字。")
        return
    elif max_value > 10000:
        await interaction.response.send_message("請輸入一個小於或等於10000的數字。")
        return

    result = random.randint(1, max_value)
    await interaction.response.send_message(f"你擲出了 {result}！")

class ServerInfoView(discord.ui.View):
    def __init__(self, guild_icon_url):
        super().__init__()
        self.guild_icon_url = guild_icon_url

    @discord.ui.button(label="點我獲得群組圖貼", style=discord.ButtonStyle.primary)
    async def send_guild_icon(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.guild_icon_url:
            await interaction.response.send_message(self.guild_icon_url)
        else:
            await interaction.response.send_message("這個伺服器沒有圖標。", ephemeral=True)

@bot.tree.command(name="server_info", description="獲取伺服器資訊")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("這個命令只能在伺服器中使用。")
        return

    try:
        owner = await guild.fetch_member(guild.owner_id)
    except discord.HTTPException:
        owner = None

    member_count = guild.member_count
    role_count = len(guild.roles)
    created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
    guild_icon_url = guild.icon.url if guild.icon else None

    owner_display = owner.mention if owner else "未知"

    embed = discord.Embed(title="伺服器資訊", color=discord.Color.blue())
    embed.add_field(name="伺服器ID", value=guild.id, inline=False)
    embed.add_field(name="擁有者", value=owner_display, inline=False)
    embed.add_field(name="成員數量", value=member_count, inline=False)
    embed.add_field(name="身分組數量", value=role_count, inline=False)
    embed.add_field(name="創建時間", value=created_at, inline=False)
    if guild_icon_url:
        embed.set_thumbnail(url=guild_icon_url)

    view = ServerInfoView(guild_icon_url)
    await interaction.response.send_message(embed=embed, view=view)

class AvatarButton(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__()
        self.user = user

    @discord.ui.button(label="獲取頭像", style=discord.ButtonStyle.primary)
    async def get_avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.user.display_avatar.url, ephemeral=True)

@bot.tree.command(name="user_info", description="獲取用戶資訊")
@app_commands.describe(user="選擇用戶")
async def user_info(interaction: discord.Interaction, user: discord.User = None):
    await interaction.response.defer()

    if user is None:
        user = interaction.user

    try:
        member = await interaction.guild.fetch_member(user.id)
    except discord.errors.NotFound:
        member = None

    created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    if member:
        embed_color = discord.Color.green()
        highest_role = member.roles[-1]
        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        server_status = f"已加入伺服器，自 {joined_at} 起"
    else:
        embed_color = discord.Color.red()
        server_status = "該用戶未加入伺服器"
    
    embed = discord.Embed(title=f"{user.name} 的用戶資訊", color=embed_color)
    embed.add_field(name="用戶名稱", value=user.name, inline=False)
    embed.add_field(name="用戶ID", value=user.id, inline=False)
    embed.add_field(name="賬號創建時間", value=created_at, inline=False)
    embed.add_field(name="伺服器狀態", value=server_status, inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    if member:
        embed.add_field(name="最高身分組", value=highest_role.name, inline=False)
    
    view = AvatarButton(user=user)
    
    await interaction.followup.send(embed=embed, view=view)

class FeedbackView(View):
    def __init__(self, interaction: discord.Interaction, message: str):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.message = message
    
    async def log_feedback(self, error_code: str = None):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(
                f"問題回報來自 {self.interaction.user} ({self.interaction.user.id}):\n"
                f"錯誤訊息: {self.message}\n"
                f"{'錯誤代號: ' + error_code if error_code else '類型: 其他問題'}\n"
                f"回報時間: {current_time}\n\n"
            )
        response_message = (
            f"感謝你的bug回饋（錯誤代號: {error_code}）。我們會檢查並修復你所提出的bug。謝謝！"
            if error_code else
            "感謝你的回饋，我們會檢查並處理你所提出的問題。謝謝！"
        )
        await self.interaction.edit_original_response(content=response_message, view=None)

    @discord.ui.button(label="指令錯誤 (203)", style=discord.ButtonStyle.primary)
    async def error_203(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.log_feedback("203")
        self.stop()

    @discord.ui.button(label="機器人訊息未回應 (372)", style=discord.ButtonStyle.primary)
    async def error_372(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.log_feedback("372")
        self.stop()

    @discord.ui.button(label="指令未回應 (301)", style=discord.ButtonStyle.primary)
    async def error_301(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.log_feedback("301")
        self.stop()

    @discord.ui.button(label="其他問題", style=discord.ButtonStyle.secondary)
    async def other_issue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.log_feedback()
        self.stop()

@bot.tree.command(name="feedback", description="bug回報")
@app_commands.describe(message="回報bug")
async def feedback(interaction: discord.Interaction, message: str):
    view = FeedbackView(interaction, message)
    await interaction.response.send_message("請選擇發生的錯誤代號:", view=view, ephemeral=True)

def parse_time(time_str):
    time_dict = {"d": 86400, "h": 3600, "m": 60}
    total_seconds = 0
    matches = re.findall(r"(\d+)([dhm])", time_str)
    for value, unit in matches:
        total_seconds += int(value) * time_dict[unit]
    return total_seconds

class GiveawayModal(discord.ui.Modal, title="設定抽獎"):
    giveaway_content = discord.ui.TextInput(label="抽獎内容", placeholder="輸入抽獎内容", required=True)
    announcement_time = discord.ui.TextInput(label="公佈時間 (格式：d/h/m)", placeholder="輸入時間，例：1d, 2h, 30m", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        content = self.giveaway_content.value
        time_input = self.announcement_time.value

        join_button = Button(label="點擊我參與抽獎", style=discord.ButtonStyle.green)
        view_participants_button = Button(label="檢視參與者", style=discord.ButtonStyle.blurple)

        async def join_button_callback(interaction: discord.Interaction):
            if interaction.user not in participants:
                participants.append(interaction.user)
                await interaction.response.send_message(f"{interaction.user.name} 已參加抽獎！", ephemeral=True)
            else:
                await interaction.response.send_message("你已經參加過這次抽獎了！", ephemeral=True)

        async def view_participants_callback(interaction: discord.Interaction):
            if participants:
                participants_list = "\n".join([user.name for user in participants])
                await interaction.response.send_message(f"當前參與者：\n{participants_list}", ephemeral=True)
            else:
                await interaction.response.send_message("目前沒有參加者。", ephemeral=True)

        join_button.callback = join_button_callback
        view_participants_button.callback = view_participants_callback

        view = View()
        view.add_item(join_button)
        view.add_item(view_participants_button)

        total_seconds = parse_time(time_input)
        announcement_timestamp = int(time.time()) + total_seconds
        await interaction.response.send_message(
            f"抽獎內容：{content}\n公佈時間：<t:{announcement_timestamp}:R>",
            view=view
        )

        await asyncio.sleep(total_seconds)

        if participants:
            winner = random.choice(participants)
            await interaction.followup.send(f"恭喜 {winner.name}！你是這次抽獎的贏家！")
            participants.clear()
        else:
            await interaction.followup.send("沒有參加者，無法進行抽獎！")

@bot.tree.command(name="start_giveaway", description="管理員設定抽獎")
@app_commands.checks.has_permissions(administrator=True)
async def start_giveaway(interaction: discord.Interaction):
    modal = GiveawayModal()
    await interaction.response.send_modal(modal)

@bot.tree.command(name="trivia", description="動漫 Trivia 問題挑戰")
async def trivia(interaction: discord.Interaction):
    question_data = get_random_question()

    question = question_data['question']
    choices = question_data['choices']
    answer = question_data['answer']

    view = discord.ui.View()
    for choice in choices:
        button = discord.ui.Button(label=choice)

        async def button_callback(interaction: discord.Interaction, choice=choice):
            if choice == answer:
                await interaction.response.send_message(f"正確！答案是：{answer}", ephemeral=True)
            else:
                await interaction.response.send_message(f"錯誤！正確答案是：{answer}", ephemeral=True)

            await interaction.message.edit(content=f"問題：{question}\n\n正確答案是：{answer}", view=None)

        button.callback = button_callback
        view.add_item(button)

    await interaction.response.send_message(f"問題：{question}", view=view)

@bot.tree.command(name="help", description="显示所有可用指令")
async def help(interaction: discord.Interaction):
    help_text = """
    ```ansi
    [2;37m[1;37m[1;36m測試員β指令[0m[1;37m[0m[2;37m[0m
    > shutdown - 關閉機器人
    > restart - 重啓機器人```
    ```ansi
    [2;37m[1;37m[1;36m[1;31m[1;31m[1;31m經濟系統[0m[1;31m[0m[1;31m[0m[1;36m[1;31m[0m[1;36m[0m[1;37m[0m[2;37m[0m
    > balance - 用戶餘額
    > work - 工作
    > pay - 轉賬```
    ```ansi
    [2;37m[1;37m[1;36m[1;34m[0m[1;36mRPG地下城冒險游戲[0m[1;37m[0m[2;37m[0m
    > rpg - 開始用戶資料
    > rpg_info - 個人資訊
    > rpg_shop - 商店街
    > rpg_adventure - 地下城冒險
    > rpg_monsterlist - 地下城怪物列表
    > rpg_itemlist - 物品列表```
         >rpg暫時停用<
    ```ansi
    [2;32m管理員指令[0m[2;32m[0m[2;32m[2;32m[2;32m[2;32m[2;32m[0m[2;32m[0m[2;32m[0m[2;32m[0m[2;32m[0m
    > ban - 封鎖用戶
    > kick - 踢出用戶
    > addmoney - 添加金錢 #比特幣
    > removemoney - 移除金錢 #比特幣
    > strat_giveaway - 開啓抽獎```
    
    ```ansi
    [2;32m普通指令[0m[2;32m[0m[2;32m[2;32m[2;32m[2;32m[2;32m[0m[2;32m[0m[2;32m[0m[2;32m[0m[2;32m[0m
    > time - 未活動的待機時間顯示
    > ping - 顯示機器人的回復延遲
    > server_info - 獲取伺服器資訊
    > user_info - 獲取用戶資訊
    > feedback - 回報錯誤
    > trivia - 問題挑戰(動漫)
    ```
    
    > `more commands is comeing soon...`
    """
    await interaction.response.send_message(help_text)

bot.run(TOKEN)
