import discord
from discord.ext import commands, tasks
import random
import requests
import json
import os
from datetime import datetime, timezone, timedelta
import pytz
import sys

TOKEN = 'token'

ALLOWED_AUTHOR_ID = 699869229712670780

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

utc_zone = pytz.utc
now_utc = datetime.now(utc_zone)
print(now_utc)

BALANCE_FILE = 'user_balance.json'
COOLDOWN_FILE = 'user_cooldown.json'

def load_balance():
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("JSON 解码错误: 确保文件格式正确")
            return {}
        except Exception as e:
            print(f"加载余额时发生错误: {e}")
            return {}
    return {}

def save_balance(balance):
    try:
        with open(BALANCE_FILE, 'w') as f:
            json.dump(balance, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存余额时发生错误: {e}")

def load_cooldown():
    if os.path.exists(COOLDOWN_FILE):
        try:
            with open(COOLDOWN_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("JSON 解码错误: 确保文件格式正确")
            return {}
        except Exception as e:
            print(f"加载冷却时间时发生错误: {e}")
            return {}
    return {}

def save_cooldown(cooldown):
    try:
        with open(COOLDOWN_FILE, 'w') as f:
            json.dump(cooldown, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存冷却时间时发生错误: {e}")

user_balance = load_balance()
user_cooldown = load_cooldown()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    change_game_status.start()

game_statuses = [
    '主人正在修復我的代碼中.',
    '主人正在修復我的代碼中..',
    '主人正在修復我的代碼中...'
]

@tasks.loop(seconds=10)
async def change_game_status():
    current_status = random.choice(game_statuses)
    await bot.change_presence(activity=discord.Game(name=current_status))

@bot.command(name='help')
async def custom_help(ctx, command_name: str = None):
    if command_name:
        command = bot.get_command(command_name)
        if command:
            help_text = f'**{command_name}**\n'
            if command.description:
                help_text += f'{command.description}\n'
            if command.usage:
                help.text += f'用法{command.usage}\n'
            await ctx.send(help_text)
        else:
            await ctx.send(f'找不到指令`{command_name}`的幫助訊息。')
    else:
     help_text = """
     **可用指令:**
     > `!help` - 顯示可用指令
     > `!ping` - 顯示機器人回復延遲
     > `!memes` - 網絡迷因
     > `!echo [message]` - 回聲
     > `!blackjack` - 21點
     > `!balance` - 查询余额
     > `!work` - 赚取金钱
     > `!shutdown` - 关闭机器人 (製作者)
     > `!restart` - 重启机器人 (製作者)
     > `!ban` - 封禁特定用戶 (管理員)
     > `!kick` - 提出用戶 (管理員)
     """
     
    if command:
        if command == 'ping':
            help_text = "`!ping` - 顯示機器人回復延遲"
        elif command == 'memes':
            help_text = "`!memes` - 網絡迷因"
        elif command == 'echo':
            help_text = "`!echo [message]` - 回聲"
        elif command == 'blackjack':
            help_text = "`!blackjack` - 21點"
        elif command == 'balance':
            help_text = "`!balance` - 查询余额"
        elif command == 'work':
            help_text = "`!work` - 赚取金钱"
        elif command == 'shutdown':
            help_text = "`!shutdown` - 关闭机器人 (製作者)"
        elif command == 'restart':
            help_text = "`!restart` - 重启机器人 (製作者)"
        elif command == 'ban':
            help_text = "`!ban [user] [reason]` - 封禁特定用戶 (管理員)"
        elif command == 'kick':
            help_text = "`!kick [user] [reason]` - 提出用戶 (管理員)"
        else:
            help_text = "未知的指令"
        
    await ctx.send(help_text)

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f'pong!: {latency:.2f} ms')

@bot.command()
async def memes(ctx):
    response = requests.get("")
    if response.status_code == 200:
        meme_url = response.json().get("image")
        await ctx.send(meme_url)
    else:
        await ctx.send("無法獲取迷因")

@bot.command()
async def work(ctx):
    user = ctx.author.id
    now = datetime.now(timezone.utc)
    
    last_work_time = user_cooldown.get(str(user))
    if last_work_time:
        last_work_time = datetime.fromisoformat(last_work_time)
        cooldown_duration = timedelta(hours=1)
        if now < last_work_time + cooldown_duration:
            time_left = (last_work_time + cooldown_duration - now).total_seconds()
            await ctx.send(f'你需要等 {int(time_left // 60)} 分钟后才能再次工作。')
            return
   
    user_cooldown[str(user)] = now.isoformat()
    save_cooldown(user_cooldown)
   
    earned_amount = random.randint(10, 100)
    user_balance[user] = user_balance.get(user, 0) + earned_amount
    save_balance(user_balance)
    
    await ctx.send(f'你赚了 {earned_amount} 比特幣! 当前余额是: {user_balance[user]} 比特幣')

@bot.command()
async def balance(ctx):
    user = ctx.author.id
    balance = user_balance.get(user, 0)
    print(f'Balance for user {user}: {balance}')
    await ctx.send(f'你的余额是: {balance} 比特幣')

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    user = ctx.author.id
    print(f'Pay command called by user {user} for {amount} to {member.id}')  # Debug output
    if amount <= 0:
        await ctx.send('金額必須大於0')
        return
    if user_balance.get(user, 0) < amount:
        await ctx.send('你的余额不足')
        return
    user_balance[user] -= amount
    user_balance[member.id] = user_balance.get(member.id, 0) + amount
    save_balance(user_balance)
    await ctx.send(f'你支付了 {amount} 比特幣給 {member.display_name}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'用戶 {member.name} 已被封禁')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'用戶 {member.name} 已被踢出')

@bot.command()
@commands.has_permissions(administrator=True)
async def addmoney(ctx, amount: int, user: discord.Member = None):
    """
    增加指定用户的余额。如果没有指定用户，则默认为增加调用者的余额。
    只有管理员可以使用这个命令。
    """
    if amount <= 0:
        await ctx.send("增加的金额必须大于0")
        return

    if user is None:
        user = ctx.author

    user_id = user.id
    if user_id not in user_balance:
        user_balance[user_id] = 0

    user_balance[user_id] += amount
    await ctx.send(f'{user.name} 的余额增加了 {amount} 比特幣! 当前余额是: {user_balance[user_id]} 比特幣')

def draw_card():
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return random.choice(cards)

def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        return int(card)

@bot.command()
async def blackjack(ctx):
    player_hand = [draw_card(), draw_card()]
    player_total = sum(card_value(card) for card in player_hand)

    dealer_hand = [draw_card(), draw_card()]
    dealer_total = sum(card_value(card) for card in dealer_hand)

    player_hand_str = ', '.join(player_hand)
    dealer_hand_str = ', '.join(dealer_hand)

    async def send_game_state():
        await ctx.send(f'你的手牌: {player_hand_str} (總計: {player_total})\n莊家的手牌: {dealer_hand_str} (總計: {dealer_total})')

    await send_game_state()

    if player_total == 21:
        await ctx.send('黑傑克！你贏了！')
        return

    class BlackjackView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.player_hand = player_hand
            self.player_total = player_total
            self.dealer_hand = dealer_hand
            self.dealer_total = dealer_total

        @discord.ui.button(label='加牌', style=discord.ButtonStyle.primary)
        async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
            new_card = draw_card()
            self.player_hand.append(new_card)
            self.player_total += card_value(new_card)
            await interaction.response.send_message(f'你抽到了: {new_card}', ephemeral=True)
            await send_game_state()
            if self.player_total > 21:
                await ctx.send('你爆牌了！莊家贏了！')
                self.stop()
            elif self.player_total == 21:
                await ctx.send('黑傑克！你贏了！')
                self.stop()

        @discord.ui.button(label='雙倍加注', style=discord.ButtonStyle.secondary)
        async def double_down(self, interaction: discord.Interaction, button: discord.ui.Button):
            new_card = draw_card()
            self.player_hand.append(new_card)
            self.player_total += card_value(new_card)
            await interaction.response.send_message(f'你抽到了: {new_card}', ephemeral=True)
            await send_game_state()
            if self.player_total == 21:
                await ctx.send('黑傑克！你贏了！')
            elif self.player_total > 21:
                await ctx.send('你爆牌了！莊家贏了！')
            else:
                await ctx.send('最終結果：\n')
                await send_game_state()
            self.stop()

        @discord.ui.button(label='棄牌', style=discord.ButtonStyle.danger)
        async def surrender(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message('你選擇了棄牌', ephemeral=True)
            self.stop()

    view = BlackjackView()
    await ctx.send('選擇你的動作:', view=view)

@bot.command()
async def restart(ctx):
    if ctx.author.id != 699869229712670780:
        await ctx.send("你不能使用該指令")
        return
    
    save_balance(user_balance)
    save_cooldown(user_cooldown)
    
    await ctx.send('正在重启机器人...')
    
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.command()
async def shutdown(ctx):
    if ctx.author.id != 699869229712670780:
        await ctx.send("你不能使用該指令")
        return
    
    save_balance(user_balance)
    save_cooldown(user_cooldown)
    
    await ctx.send('正在关闭机器人...')
    
    await bot.close()

@bot.command()
async def roll(ctx, sides: int = 100):
    """
    Roll a dice with a specified number of sides (default is 100).
    """
    if sides <= 0:
        await ctx.send("骰子的面数必须大于0")
        return

    roll_result = random.randint(1, sides)
    await ctx.send(f'你掷了一个 {sides} 面的骰子，结果是: {roll_result}')

bot.run(TOKEN)
