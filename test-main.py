import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import random
import json
from datetime import datetime, timedelta
import asyncio
from discord.ui import Select, Button, View, Modal, TextInput
import subprocess
import time
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse
from pydantic_core import InitErrorDetails
import yaml
from discord import SelectOption
from discord import ui
import subprocess
import psutil
from home_work import parse_requirement
import calculator
import math
from calendar_module import add_event, remove_event, get_user_events, check_events, CalendarEvent
from omikuji import draw_lots
import re 

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN_TEST_BOT')
AUTHOR_ID = int(os.getenv('AUTHOR_ID'))
LOG_FILE_PATH = "test_bot_feedback_log.txt"

logging.basicConfig(level=logging.INFO)

error_logger = logging.getLogger('discord')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(filename='error.log', encoding='utf-8', mode='w')
error_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
error_logger.addHandler(error_handler)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
user_messages = {}
participants = []

bot = commands.Bot(command_prefix='/', intents=intents)

user_balance = {}

def save_balance(data):
    with open('balance.yml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

def load_balance():
    if os.path.exists('balance.yml'):
        try:
            with open('balance.yml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print("Error loading balance.yml:", e)
            with open('balance.yml', 'r', encoding='utf-8') as f:
                print("Problematic file contents:")
                print(f.read())
    return {}

user_balance = load_balance()

with open('fishi.yml', 'r', encoding='utf-8') as file:
    fish_data = yaml.safe_load(file)

with open('fishi_shop.yml', 'r', encoding='utf-8') as file:
    shop_data = yaml.safe_load(file)

def save_data(data, filename="candyrank.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_data(filename="candyrank.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

candy_collection = load_data()

trick_cooldown = {}
daily_trick_count = {}
daily_reset_time = {}
last_candy_collect = {}
cooldowns = {}

def reset_daily_limit(user_id):
    now = datetime.now()
    if user_id in daily_reset_time and daily_reset_time[user_id].date() != now.date():
        daily_trick_count[user_id] = 0
        daily_reset_time[user_id] = now

def load_cooldown_data(cooldown_file):
    try:
        with open(cooldown_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cooldown_data(data, cooldown_file):
    with open(cooldown_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def is_on_cooldown(user_id, cooldown_file, cooldown_hours):
    cooldown_data = load_cooldown_data(cooldown_file)
    if str(user_id) in cooldown_data:
        last_used = datetime.fromisoformat(cooldown_data[str(user_id)])
        if datetime.now() - last_used < timedelta(hours=cooldown_hours):
            remaining = timedelta(hours=cooldown_hours) - (datetime.now() - last_used)
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes = remainder // 60
            return True, f"{hours} 小時 {minutes} 分鐘"
    return False, None

def update_cooldown(user_id, cooldown_file):
    cooldown_data = load_cooldown_data(cooldown_file)
    cooldown_data[str(user_id)] = datetime.now().isoformat()
    save_cooldown_data(cooldown_data, cooldown_file)

def load_config():
    if not os.path.exists("config.yml"):
        default_config = {
            "mention_counts": {}
        }
        save_config(default_config)
        return default_config

    with open("config.yml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def save_config(config):
    with open("config.yml", "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file)

config = load_config()
mention_counts = config.get("mention_counts", {})

@bot.event
async def on_ready():
    print(f'已登入 {bot.user.name}')
    
    await bot.change_presence(
        status=discord.Status.idle,
        activity = discord.Activity(type=discord.ActivityType.listening, name="No Dazzle, No Braek feat:Rappa")
    )
    
    try:
        synced = await bot.tree.sync()
        print(f'成功同步 {len(synced)} 个命令')
    except Exception as e:
        print(f'同步命令时出错: {e}')
        error_logger.error(f'同步命令时出错: {e}', exc_info=True)
    
        last_activity_time = time.time()
        check_events.start(bot)

@bot.event
async def on_message(message):
    global last_activity_time
    last_activity_time = time.time()
    user_id = str(message.author.id)
    guild_id = str(message.guild.id)
    if message.author == bot.user:
        return

    content_lower = message.content.lower()
    if '關於芙蘭' in content_lower:
        await message.channel.send('芙蘭的創建時間是<t:1722340500:D>')

    elif '芙蘭閑置多久了' in content_lower:
        idle_minutes = (time.time() - last_activity_time) / 60
        await message.channel.send(f'芙蘭目前閑置時間為 {idle_minutes:.2f} 分鐘。')

    elif '關於製作者' in content_lower:
        await message.channel.send('製作者是個很好的人 雖然看上去有點怪怪的')

    elif '芙蘭的生日' in content_lower:
        await message.channel.send('機器人芙蘭的生日在<t:1722340500:D>')

    elif '熊貓' in content_lower:
        await message.channel.send('Miya253:幹嘛 我現在在修著幽幽子 有事情的話請DM我 謝謝')

    elif message.content.startswith('關閉芙蘭'):
        if message.author.id == AUTHOR_ID:
            await message.channel.send("正在關閉...")
            await asyncio.sleep(5)
            await bot.close()
        else:
            await message.channel.send("你無權關閉我 >_<")

    elif message.content.startswith('重啓芙蘭'):
        if message.author.id == AUTHOR_ID:
            await message.channel.send("正在重啟芙蘭...")
            subprocess.Popen([sys.executable, os.path.abspath(__file__)])
            await bot.close()
        else:
            await message.channel.send("你無權重啓我 >_<")

    elif "抽籤" in message.content:
        result = draw_lots()
        await message.channel.send(f"你抽出的御神籤的結果是:\n{result}")
        
    if message.author == message.guild.owner or any(role.permissions.administrator for role in message.author.roles):
        await bot.process_commands(message)
        return
    
    if message.author.bot and ("@everyone" in message.content or "@here" in message.content):
        try:
            await message.channel.send(f"{message.author.mention} 被檢測到濫用全體標註，將被直接踢出或封禁。")
            await message.author.ban(reason="濫用全體標註")
        except discord.Forbidden:
            await message.channel.send(f"無法封禁 {message.author.mention}，請求管理員提高機器人權限。")
        return
    
    if "@everyone" in message.content or "@here" in message.content:
        if user_id not in mention_counts:
            mention_counts[user_id] = 1
        else:
            mention_counts[user_id] += 1

        if mention_counts[user_id] == 1:
            await message.channel.send(f"{message.author.mention} 請勿使用全體標註！這是您的第一次警告。")

        elif mention_counts[user_id] == 2:
            await message.channel.send(f"{message.author.mention} 已經多次使用全體標註，將被踢出伺服器。")
            try:
                await message.author.kick(reason="多次使用全體標註")
            except discord.Forbidden:
                await message.channel.send(f"無法踢出 {message.author.mention}，請求管理員提高機器人權限。")

        elif mention_counts[user_id] >= 3:
            await message.channel.send(f"{message.author.mention} 已被永久封禁。")
            try:
                await message.author.ban(reason="多次使用全體標註")
            except discord.Forbidden:
                await message.channel.send(f"無法封禁 {message.author.mention}，請求管理員提高機器人權限。")
                
        await message.delete()
        return
    
    await bot.process_commands(message)

@bot.tree.command(name="shutdown", description="关闭芙蘭")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == AUTHOR_ID:
        await interaction.response.send_message("关闭中...")
        await bot.close()
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="restart", description="重启芙蘭")
async def restart(interaction: discord.Interaction):
    if interaction.user.id == AUTHOR_ID:
        await interaction.response.defer()
        await interaction.followup.send("重启中...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="balance", description="查询你的幽灵币余额")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    try:
        with open('balance.yml', 'r') as file:
            balances = yaml.safe_load(file)
        
        user_balance = balances.get(user_id, 0)
        await interaction.response.send_message(f"你的幽灵币余额为: {user_balance}")
    except FileNotFoundError:
        await interaction.response.send_message("balance.yml 文件未找到，无法查询余额。")

@bot.tree.command(name="addmoney", description="给用户增加幽靈幣（管理员专用）")
async def addmoney(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.guild_permissions.administrator:
        recipient_id = str(member.id)
        user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
        save_balance(user_balance)
        await interaction.response.send_message(f'给 {member.name} 增加了 {amount} 幽靈幣。')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="rpg_start", description="初始化角色数据")
async def rpg_start(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = {
        'lv': 1,
        'exp': 0,
        'hp': 100,
        'mp': 50,
        'stamina': 50
    }

    if not os.path.exists('rpg-data'):
        os.makedirs('rpg-data')

    with open(f'rpg-data/{user_id}.yml', 'w') as file:
        yaml.dump(data, file)

    await interaction.response.send_message("角色已初始化，开始你的冒险吧！")

@bot.tree.command(name="rpg_info", description="查看角色信息")
async def rpg_info(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    try:
        with open(f'rpg-data/{user_id}.yml', 'r') as file:
            player_data = yaml.safe_load(file)
        await interaction.response.send_message(
            f"等級: {player_data['lv']}\n"
            f"生命: {player_data['hp']}\n"
            f"魔力: {player_data['mp']}\n"
            f"體力: {player_data['stamina']}"
        )
    except FileNotFoundError:
        await interaction.response.send_message("你还没有初始化角色，请使用 `/rpg_start` 初始化。")

@bot.tree.command(name="rpg_backpack", description="开启背包")
async def rpg_backpack(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    try:
        with open(f'backpack/{user_id}.yml', 'r') as file:
            backpack = yaml.safe_load(file)
        
        options = [SelectOption(label=item, description=f"数量: {backpack[item]['quantity']}") for item in backpack]
        select = discord.ui.Select(placeholder="选择一个物品查看详情", options=options)

        async def select_callback(interaction: discord.Interaction):
            selected_item = select.values[0]
            item_info = backpack[selected_item]
            await interaction.response.send_message(f"你选择了: {selected_item}\n"
                                                    f"数量: {item_info['quantity']}\n"
                                                    f"描述: {item_info.get('description', '无描述')}")
        
        select.callback = select_callback
        view = View()
        view.add_item(select)

        await interaction.response.send_message("请选择一个物品:", view=view)

    except FileNotFoundError:
        await interaction.response.send_message("你的背包是空的。")

class ShopSelect(Select):
    def __init__(self, shop_items):
        options = [
            discord.SelectOption(label="鐵匠鋪", description="武器和裝備"),
            discord.SelectOption(label="魔法舖", description="魔法用品"),
            discord.SelectOption(label="小吃舖", description="恢復物品")
        ]
        super().__init__(placeholder="選擇商店", options=options)
        self.shop_items = shop_items

    async def callback(self, interaction: discord.Interaction):
        shop = self.values[0]
        items = self.shop_items.get(shop, [])
        
        if not items:
            await interaction.response.send_message(f"{shop}暂时没有商品", ephemeral=True)
            return
        
        buttons = []
        for item in items:
            button = Button(label=f"{item['name']} - {item['price']} BTC", style=discord.ButtonStyle.primary)
            button.callback = self.create_purchase_callback(item, interaction.user.id)
            buttons.append(button)
        
        view = View()
        for btn in buttons:
            view.add_item(btn)
        await interaction.response.send_message(f"你选择了 {shop}，以下是可购买的商品：", view=view)

    def create_purchase_callback(self, item, user_id):
        async def purchase_callback(interaction: discord.Interaction):
            modal = PurchaseModal(item, user_id)
            await interaction.response.send_modal(modal)
        return purchase_callback

class PurchaseModal(Modal):
    def __init__(self, item, user_id):
        super().__init__(title="购买物品")
        self.item = item
        self.user_id = user_id
        self.add_item(TextInput(label="输入购买数量", placeholder="请输入数量", min_length=1, max_length=10))

    async def on_submit(self, interaction: discord.Interaction):
        quantity = int(self.children[0].value)
        total_cost = quantity * self.item['price']

        try:
            with open('balance.yml', 'r') as balance_file:
                balances = yaml.safe_load(balance_file)
        except FileNotFoundError:
            balances = {}

        user_balance = balances.get(str(self.user_id), 0)

        if user_balance < total_cost:
            await interaction.response.send_message(f"你的幽灵币余额不足，无法购买 {quantity} 个 {self.item['name']}。")
            return

        balances[str(self.user_id)] = user_balance - total_cost

        with open('balance.yml', 'w') as balance_file:
            yaml.dump(balances, balance_file)

        backpack_path = f'backpack/{self.user_id}.yml'
        try:
            with open(backpack_path, 'r') as backpack_file:
                backpack = yaml.safe_load(backpack_file)
        except FileNotFoundError:
            backpack = {}

        if self.item['name'] in backpack:
            backpack[self.item['name']]['quantity'] += quantity
        else:
            backpack[self.item['name']] = {
                'quantity': quantity,
                'description': self.item.get('description', '无描述')
            }

        with open(backpack_path, 'w') as backpack_file:
            yaml.dump(backpack, backpack_file)

        await interaction.response.send_message(f"你购买了 {quantity} 个 {self.item['name']}，共花费 {total_cost} 幽灵币。物品已添加到你的背包。")

@bot.tree.command(name="rpg_shop", description="前往商店")
async def rpg_shop(interaction: discord.Interaction):
    with open('shop_item.yml', 'r', encoding='utf-8') as file:
        shop_items = yaml.safe_load(file)
    
    view = View()
    view.add_item(ShopSelect(shop_items))
    
    await interaction.response.send_message("欢迎来到商店，请选择你要访问的店铺：", view=view)

@bot.tree.command(name="rpg_adventure", description="开起冒险")
async def rpg_adventure(interaction: discord.Interaction):
    try:
        with open('dungeon.yml', 'r') as dungeon_file:
            dungeon_data = yaml.safe_load(dungeon_file)
        with open('monster_item.yml', 'r') as monster_item_file:
            monster_items = yaml.safe_load(monster_item_file)
        with open('monster.yml', 'r') as monster_file:
            monsters = yaml.safe_load(monster_file)
        
        await interaction.response.send_message("冒险开始！")
    
    except FileNotFoundError as e:
        missing_file = str(e).split("'")[1]
        
        embed = discord.Embed(
            title="錯誤: 文件丟失",
            description=f"文件 `{missing_file}` 丟失，請聯繫作者以解決此問題。",
            color=discord.Color.red()
        )
        embed.add_field(name="GitHub", value="[點擊這裡聯繫作者](https://github.com/xuemeng1987)")
        embed.set_footer(text="感謝您的理解！")

        await interaction.response.send_message(embed=embed)

class Battle:
    def __init__(self, challenger_data, opponent_data):
        self.challenger_data = challenger_data
        self.opponent_data = opponent_data
        self.turns = 30

    def perform_attack(self, attacker, defender):
        attack_value = random.randint(1, 10) * attacker['lv']
        defender['hp'] -= attack_value
        return attack_value

    def is_over(self):
        return self.challenger_data['hp'] <= 0 or self.opponent_data['hp'] <= 0 or self.turns == 0

    def get_winner(self):
        if self.challenger_data['hp'] > 0 and self.opponent_data['hp'] > 0:
            return "平局"
        if self.challenger_data['hp'] > 0:
            return "挑战者"
        return "对手"

@bot.tree.command(name="rpg_playerbattle", description="与其他玩家决斗")
async def rpg_playerbattle(interaction: discord.Interaction, opponent: discord.Member):
    if interaction.user.id == opponent.id:
        await interaction.response.send_message("你不能和自己决斗！")
        return

    challenger_data_path = f'rpg-data/{interaction.user.id}.yml'
    opponent_data_path = f'rpg-data/{opponent.id}.yml'

    try:
        with open(challenger_data_path, 'r') as challenger_file:
            challenger_data = yaml.safe_load(challenger_file)
        with open(opponent_data_path, 'r') as opponent_file:
            opponent_data = yaml.safe_load(opponent_file)
    except FileNotFoundError:
        await interaction.response.send_message("无法找到玩家数据，请确保双方都已初始化角色。")
        return

    battle = Battle(challenger_data, opponent_data)

    for turn in range(battle.turns):
        attack_value = battle.perform_attack(challenger_data, opponent_data)
        if battle.is_over():
            break
        battle.perform_attack(opponent_data, challenger_data)
        if battle.is_over():
            break

    winner = battle.get_winner()

    await interaction.response.send_message(f"决斗结束！胜者是：{winner}")

def get_item_prices():
    try:
        with open('monster_item_shell_price.yml', 'r', encoding='utf-8') as file:
            item_prices = yaml.safe_load(file)
        return item_prices
    except Exception as e:
        print(f"Error loading item prices: {e}")
        return None

@bot.tree.command(name="rpg_shell", description="出售怪物掉落物品")
async def rpg_shell(interaction: discord.Interaction):
    item_prices = get_item_prices()
    
    if not item_prices:
        await interaction.response.send_message("无法加载物品价格数据。", ephemeral=True)
        return

    options = [discord.SelectOption(label=item, description=f"价格: {price}") for item, price in item_prices.items()]
    
    select = discord.ui.Select(placeholder="选择要出售的物品", options=options)
    
    async def select_callback(select_interaction: discord.Interaction):
        selected_item = select.values[0]
        price = item_prices.get(selected_item, "未知价格")
        
        class ConfirmView(discord.ui.View):
            @discord.ui.button(label="确认出售", style=discord.ButtonStyle.green)
            async def confirm_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                user_id = str(interaction.user.id)
                try:
                    with open('balance.yml', 'r') as balance_file:
                        balances = yaml.safe_load(balance_file)
                except FileNotFoundError:
                    balances = {}
                
                user_balance = balances.get(user_id, 0)
                balances[user_id] = user_balance + price
                
                with open('balance.yml', 'w') as balance_file:
                    yaml.safe_dump(balances, balance_file)
                
                backpack_path = f'backpack/{user_id}.yml'
                try:
                    with open(backpack_path, 'r') as backpack_file:
                        backpack = yaml.safe_load(backpack_file)
                except FileNotFoundError:
                    backpack = {}

                if selected_item in backpack:
                    backpack[selected_item]['quantity'] -= 1
                    if backpack[selected_item]['quantity'] <= 0:
                        del backpack[selected_item]
                
                with open(backpack_path, 'w') as backpack_file:
                    yaml.safe_dump(backpack, backpack_file)
                
                await button_interaction.response.send_message(f"你成功出售了 **{selected_item}**，价格为 **{price}** 幽灵币。")
        
        view = ConfirmView()
        await select_interaction.response.send_message(f"你选择了 **{selected_item}**，价格为 **{price}** 幽灵币。是否确认出售？", view=view)
    
    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    
    await interaction.response.send_message("请选择你想出售的物品：", view=view)

class NPC:
    def __init__(self, name):
        self.name = name

lei_yao = NPC

class LoanModal(discord.ui.Modal, title="貸款申請"):
    amount = discord.ui.TextInput(label="請輸入想借的幽靈幣數量", placeholder="輸入數字", required=True)

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        try:
            loan_amount = int(self.amount.value)
            loan_date = datetime.now()
            
            try:
                with open('loan.yml', 'r') as file:
                    loans = yaml.safe_load(file) or {}
            except FileNotFoundError:
                loans = {}

            loans[user_id] = {
                'loan_amount': loan_amount,
                'loan_date': loan_date.strftime('%Y-%m-%d %H:%M:%S')
            }

            with open('loan.yml', 'w') as file:
                yaml.safe_dump(loans, file)

            await interaction.response.send_message(f"雷燿說：你借了 {loan_amount} 幽靈幣，請記得按時還款哦！")

        except ValueError:
            await interaction.response.send_message("雷燿說：請輸入一個有效的數字！")

class RepayLoanModal(discord.ui.Modal, title="還款"):
    repayment_amount = discord.ui.TextInput(
        label="請輸入還款金額", 
        placeholder="輸入數字", 
        required=True
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        try:
            with open('loan.yml', 'r') as file:
                loans = yaml.safe_load(file) or {}
            
            if user_id not in loans:
                await interaction.response.send_message("雷燿說：你沒有貸款記錄！")
                return
            
            loan_info = loans[user_id]
            loan_amount = loan_info['loan_amount']
            loan_date_str = loan_info['loan_date']
            loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d %H:%M:%S')

            current_date = datetime.now()
            days_passed = (current_date - loan_date).days

            interest_rate_per_day = 0.01
            total_repay_amount = loan_amount * (1 + interest_rate_per_day * days_passed)

            with open('balance.yml', 'r') as file:
                balances = yaml.safe_load(file) or {}

            user_balance = balances.get(user_id, 0)

            if user_balance >= total_repay_amount:
                balances[user_id] = user_balance - total_repay_amount

                with open('balance.yml', 'w') as file:
                    yaml.safe_dump(balances, file)

                del loans[user_id]
                with open('loan.yml', 'w') as file:
                    yaml.safe_dump(loans, file)

                await interaction.response.send_message(f"雷燿說：你已成功還款 {total_repay_amount:.2f} 幽靈幣，謝謝你的信任！")

            else:
                await interaction.response.send_message(f"雷燿說：你的餘額不足以償還 {total_repay_amount:.2f} 幽靈幣！")

        except FileNotFoundError:
            await interaction.response.send_message("雷燿說：銀行資料未找到，無法完成還款。")
        except Exception as e:
            await interaction.response.send_message(f"雷燿說：發生錯誤：{str(e)}")

class BankView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="查詢餘額", style=discord.ButtonStyle.green)
    async def check_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        try:
            with open('balance.yml', 'r') as file:
                balances = yaml.safe_load(file) or {}

            user_balance = balances.get(user_id, 0)
            await interaction.response.send_message(f"雷燿告訴你：你的餘額為 {user_balance} 幽靈幣。")
        
        except FileNotFoundError:
            await interaction.response.send_message("雷燿說：銀行資料未找到，無法查詢餘額。")

    @discord.ui.button(label="貸款", style=discord.ButtonStyle.blurple)
    async def loan(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LoanModal())

    @discord.ui.button(label="還款", style=discord.ButtonStyle.red)
    async def repay_loan(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RepayLoanModal())

@bot.tree.command(name="rpg_bank", description="與雷燿互動，查詢餘額或貸款")
async def rpg_bank(interaction: discord.Interaction):
    view = BankView()
    await interaction.response.send_message("雷燿問：你想查詢餘額、貸款還是還款？", view=view)

@bot.tree.command(name="system_status", description="检查机器人的系统资源使用情况")
async def system_status(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 你没有权限使用此命令。此命令仅限管理员使用。", ephemeral=True)
        return

    await interaction.response.defer()

    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024 ** 3)
    used_memory = memory_info.used / (1024 ** 3)
    free_memory = memory_info.available / (1024 ** 3)

    status_message = (
        f"**🖥️ 系统资源使用情况：**\n"
        f"```css\n"
        f"CPU 使用率  : {cpu_percent}%\n"
        f"总内存      : {total_memory:.2f} GB\n"
        f"已用内存    : {used_memory:.2f} GB\n"
        f"可用内存    : {free_memory:.2f} GB\n"
        f"```\n"
    )

    await interaction.followup.send(status_message)

@bot.tree.command(name="help_work", description="解析需求並返回生成的Python代碼")
async def help_work(interaction: discord.Interaction, requirement: str):
    """
    處理 /help_work 命令，並將解析的代碼返回給用戶
    :param interaction: discord.Interaction - 命令的上下文
    :param requirement: str - 用戶輸入的需求
    """
    code = parse_requirement(requirement)
    await interaction.response.send_message(f"根據你的需求生成的代碼是:\n```python\n{code}\n```")

class OperationSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='加法', value='add', description='進行加法運算'),
            discord.SelectOption(label='減法', value='subtract', description='進行減法運算'),
            discord.SelectOption(label='乘法', value='multiply', description='進行乘法運算'),
            discord.SelectOption(label='除法', value='divide', description='進行除法運算'),
            discord.SelectOption(label='次方', value='power', description='進行指數運算'),
            discord.SelectOption(label='平方根', value='sqrt', description='計算平方根'),
            discord.SelectOption(label='對數', value='log', description='計算對數'),
            discord.SelectOption(label='正弦', value='sin', description='計算正弦'),
            discord.SelectOption(label='餘弦', value='cos', description='計算餘弦'),
            discord.SelectOption(label='正切', value='tan', description='計算正切'),
            discord.SelectOption(label='圓柱體積', value='cylinder_volume', description='計算圓柱體積'),
            discord.SelectOption(label='圓面積', value='circle_area', description='計算圓的面積'),
            discord.SelectOption(label='三角形面積', value='triangle_area', description='計算三角形面積'),
            discord.SelectOption(label='球體積', value='sphere_volume', description='計算球的體積'),
            discord.SelectOption(label='斜邊長度', value='hypotenuse', description='計算直角三角形的斜邊'),
            discord.SelectOption(label='速度', value='speed', description='計算速度'),
        ]
        super().__init__(placeholder='選擇一個運算', options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CalculatorModal(self.values[0]))

def preprocess_input(value):
    if value == '' or value is None:
        return None

    value = value.lower()

    if "h" in value:  # 小時轉換為秒
        value = value.replace("h", "")
        return float(value) * 3600
    
    if "m" in value:  # 分鐘轉換為秒
        value = value.replace("m", "")
        return float(value) * 60
    
    if "s" in value:  # 秒保持不變
        value = value.replace("s", "")
        return float(value)
    
    # 處理圓周率符號
    value = value.replace("π", str(math.pi))
    
    # 處理長度單位，比如 cm 可以添加更多單位處理
    value = value.replace("cm", "")  # 目前直接移除cm單位
    return float(value)

class CalculatorModal(Modal):
    def __init__(self, operation):
        super().__init__(title="輸入數字")
        self.operation = operation

        self.add_item(TextInput(label="數字 1", placeholder="輸入第一個數字", required=True))
        
        # 根據不同的操作，要求輸入第二個數字
        if operation in ['add', 'subtract', 'multiply', 'divide', 'power', 'hypotenuse']:
            self.add_item(TextInput(label="數字 2（可選）", placeholder="輸入第二個數字", required=False))

        # 特殊運算需要高度或底
        if operation in ['cylinder_volume', 'triangle_area']:
            self.add_item(TextInput(label="高度（可選）", placeholder="與高度相關的運算", required=False))

        if operation == 'triangle_area':
            self.add_item(TextInput(label="底（可選）", placeholder="與底相關的運算", required=False))
        
        if operation == 'speed':
            self.add_item(TextInput(label="時間", placeholder="輸入時間", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            num1 = preprocess_input(self.children[0].value)
            num2 = preprocess_input(self.children[1].value if len(self.children) > 1 else None)
            height = preprocess_input(self.children[2].value if len(self.children) > 2 else None)
            base = preprocess_input(self.children[3].value if len(self.children) > 3 else None)
            time = preprocess_input(self.children[4].value if len(self.children) > 4 else None)

            result = calculator.perform_operation(self.operation, num1, num2, height, base, time)
            await interaction.response.send_message(f'運算結果：{result}')

        except ValueError:
            await interaction.response.send_message(f"輸入的數據無效，請檢查後再試！", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"發生錯誤：{str(e)}", ephemeral=True)

class CalculatorView(View):
    def __init__(self):
        super().__init__()
        self.add_item(OperationSelect())

@bot.tree.command(name="calculate", description="進行高級數學運算")
async def calculate(interaction: discord.Interaction):
    await interaction.response.send_message("請選擇一個運算：", view=CalculatorView())

@bot.tree.command(name="create_event", description="創建一個新的事件")
@app_commands.describe(event_name="事件名稱", event_date="事件日期 (YYYY-MM-DD)", event_time="事件時間 (HH:MM)", reminder_time="提醒時間 (分鐘)", description="事件描述")
async def create_event(interaction: discord.Interaction, event_name: str, event_date: str, event_time: str, reminder_time: int = 10, description: str = ""):
    try:
        event_date_time = datetime.datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")
        user_id = interaction.user.id
        new_event = CalendarEvent(event_name, event_date_time, user_id, description, reminder_time)
        add_event(new_event)
        await interaction.response.send_message(f"事件 `{event_name}` 已創建，將在 {event_date_time} 開始！")
    except ValueError:
        await interaction.response.send_message("日期或時間格式不正確，請使用 `YYYY-MM-DD` 和 `HH:MM` 格式。")

@bot.tree.command(name="delete_event", description="刪除一個已創建的事件")
@app_commands.describe(event_name="事件名稱")
async def delete_event(interaction: discord.Interaction, event_name: str):
    user_id = interaction.user.id
    remove_event(event_name, user_id)
    await interaction.response.send_message(f"事件 `{event_name}` 已刪除。")

@bot.tree.command(name="list_events", description="列出所有已創建的事件")
async def list_events(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_events = get_user_events(user_id)
    if user_events:
        events_details = "\n".join([f"{event.event_name}: {event.event_date_time} (提醒: {event.reminder_time} 分鐘前)" for event in user_events])
        await interaction.response.send_message(f"您的事件:\n{events_details}")
    else:
        await interaction.response.send_message("您目前沒有設置任何事件。")

@bot.tree.command(name="draw_lots", description="抽取御神抽籤")
async def draw_lots_command(interaction: discord.Interaction):
    cooldown_file = "cooldowns.json"
    cooldown_hours = 5
    user_id = interaction.user.id
    
    on_cooldown, remaining_time = is_on_cooldown(user_id, cooldown_file, cooldown_hours)
    
    if on_cooldown:
        await interaction.response.send_message(f"你還在冷卻中，剩餘時間：{remaining_time}", ephemeral=True)
    else:
        await interaction.response.defer()
        result = draw_lots()
        await interaction.followup.send(f"你抽出的御神籤的結果是:\n{result}")
        update_cooldown(user_id, cooldown_file)

bot.run(TOKEN)
