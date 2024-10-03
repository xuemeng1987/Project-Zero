from turtle import title
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
import yaml
from discord import SelectOption
from discord import ui
import subprocess
import psutil

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

# 從 `candyrank.json` 讀取數據的函數
def load_data(filename="candyrank.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

# 初始化數據
candy_collection = load_data()

@bot.event
async def on_ready():
    print(f'已登入 {bot.user.name}')
    
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="debug bot Mk.2 芙蘭")
    )
    
    try:
        synced = await bot.tree.sync()
        print(f'成功同步 {len(synced)} 个命令')
    except Exception as e:
        print(f'同步命令时出错: {e}')
        error_logger.error(f'同步命令时出错: {e}', exc_info=True)
    
        last_activity_time = time.time()

@bot.event
async def on_message(message):
    global last_activity_time
    last_activity_time = time.time()
    user_id = str(message.author.id)
    
    if message.author == bot.user:
        return

    content_lower = message.content.lower()

    if '關於芙蘭' in content_lower:
        await message.channel.send('芙蘭的創建時間是<t:1722340500:D>')
    
    if '芙蘭閑置多久了' in content_lower:
        idle_seconds = time.time() - last_activity_time
        idle_minutes = idle_seconds / 60
        await message.channel.send(f'芙蘭目前閑置時間為 {idle_minutes:.2f} 分鐘。')
    
    if '關於製作者' in content_lower:
        await message.channel.send('製作者是個很好的人 雖然看上去有點怪怪的')
    
    if '芙蘭的生日' in content_lower:
        await message.channel.send('機器人芙蘭的生日在<t:1722340500:D>')

    if '熊貓' in content_lower:
        await message.channel.send('Miya253:幹嘛 我現在在修著幽幽子 有事情的話請DM我 謝謝')
    
    if message.content.startswith('關閉芙蘭'):
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
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    error_logger.error(f'指令錯誤：{ctx.command} - {error}', exc_info=True)
    await ctx.send('發生了錯誤，請檢查命令並重試。')

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
        await interaction.response.send_message("重启中...")
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

class ShopView(discord.ui.View):
    def __init__(self, user_id, fish_list):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.selected_fish = None
        self.fish_list = fish_list

        if self.fish_list:
            options = [
                discord.SelectOption(
                    label=f"{fish['name']} - 大小: {fish['size']:.2f} 公斤", 
                    description=f"估價: {self.calculate_fish_value(fish)} 幽靈幣"
                )
                for fish in self.fish_list
            ]
        else:
            options = []

        select = discord.ui.Select(
            placeholder="選擇你想出售的魚",
            options=options,
            disabled=not bool(self.fish_list),
            custom_id="fish_select"
        )
        select.callback = self.select_fish_to_sell
        self.add_item(select)

    async def select_fish_to_sell(self, interaction: discord.Interaction):
        selected_fish_value = interaction.data['values'][0]
        self.selected_fish = next(fish for fish in self.fish_list if f"{fish['name']} - 大小: {fish['size']:.2f} 公斤" == selected_fish_value)
        
        await interaction.response.edit_message(content=f"你選擇了出售: {self.selected_fish['name']} ({self.selected_fish['size']} 公斤)", 
                                                view=SellView(self.user_id, self.selected_fish, self.fish_list))

    def calculate_fish_value(self, fish):
        base_value = 50 if fish['rarity'] == 'common' else 100 if fish['rarity'] == 'uncommon' else 200 if fish['rarity'] == 'rare' else 500
        return int(base_value * fish['size'])

class SellView(discord.ui.View):
    def __init__(self, user_id, selected_fish, fish_list):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.selected_fish = selected_fish
        self.fish_list = fish_list

    @discord.ui.button(label="出售", style=discord.ButtonStyle.secondary)
    async def sell_fish(self, interaction: discord.Interaction, button: discord.ui.Button):
        fish_to_sell = self.selected_fish
        sell_price = self.calculate_fish_value(fish_to_sell)

        with open('fishiback.yml', 'r', encoding='utf-8') as file:
            fish_back = yaml.safe_load(file)

        user_data = fish_back[self.user_id]
        user_data['balance'] += sell_price
        user_data['caught_fish'].remove(fish_to_sell)

        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump(fish_back, file)

        user_fish_list = fish_back[self.user_id]['caught_fish']
        
        if user_fish_list:
            await interaction.response.edit_message(
                content=f"✅ 你成功出售了 {fish_to_sell['name']}，獲得了 {sell_price} 幽靈幣！\n\n請選擇你想出售的其他漁獲：",
                view=ShopView(self.user_id, user_fish_list)
            )
        else:
            await interaction.response.edit_message(
                content=f"✅ 你成功出售了 {fish_to_sell['name']}，獲得了 {sell_price} 幽靈幣！\n\n你已經沒有其他漁獲可以出售了。",
                view=None
            )

    def calculate_fish_value(self, fish):
        base_value = 50 if fish['rarity'] == 'common' else 100 if fish['rarity'] == 'uncommon' else 200 if fish['rarity'] == 'rare' else 500
        return int(base_value * fish['size'])


@bot.tree.command(name="fish_shop", description="查看釣魚商店並購買或出售漁獲")
async def fish_shop(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    with open('fishiback.yml', 'r', encoding='utf-8') as file:
        fish_back = yaml.safe_load(file)

    user_fish_list = fish_back.get(user_id, {}).get('caught_fish', [])
    
    if not user_fish_list:
        await interaction.response.send_message("🎣 你沒有漁獲可以出售。", ephemeral=True)
        return

    await interaction.response.send_message("🎣 歡迎來到釣魚商店！請選擇並出售你的漁獲：", view=ShopView(user_id, user_fish_list))

def catch_fish():
    fish = random.choice(fish_data['fish'])
    size = round(random.uniform(fish['min_size'], fish['max_size']), 2)
    return {
        'name': fish['name'],
        'rarity': fish['rarity'],
        'size': size
    }

class FishView(discord.ui.View):
    def __init__(self, fish, user_id):
        super().__init__(timeout=None)
        self.fish = fish
        self.user_id = user_id

    @discord.ui.button(label="保存漁獲", style=discord.ButtonStyle.primary)
    async def save_fish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not os.path.exists('fishiback.yml'):
            with open('fishiback.yml', 'w', encoding='utf-8') as file:
                yaml.dump({}, file)

        with open('fishiback.yml', 'r', encoding='utf-8') as file:
            fish_back = yaml.safe_load(file)

        if self.user_id not in fish_back:
            fish_back[self.user_id] = {'balance': 0, 'caught_fish': []}

        user_data = fish_back[self.user_id]
        user_data['caught_fish'].append(self.fish)

        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump(fish_back, file)

        await interaction.response.send_message(f"✅ 你成功保存了 {self.fish['name']} ({self.fish['size']} 公斤) 到你的漁獲列表中！", ephemeral=True)

    @discord.ui.button(label="再釣多一次", style=discord.ButtonStyle.secondary)
    async def fish_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_fish = catch_fish()
        self.fish = new_fish
        await interaction.response.send_message(
            content=f"🎣 你捕到了一條 {new_fish['rarity']} 的 {new_fish['name']}！它的大小是 {new_fish['size']} 公斤！",
            view=FishView(new_fish, self.user_id)
    )

@bot.tree.command(name="fish", description="進行一次釣魚")
async def fish(interaction: discord.Interaction):
    fish_caught = catch_fish()
    user_id = str(interaction.user.id)

    await interaction.response.send_message(f"🎣 你捕到了一條 {fish_caught['rarity']} 的 {fish_caught['name']}！它的大小是 {fish_caught['size']} 公斤！",
                                            view=FishView(fish_caught, user_id))

@bot.tree.command(name="fish_back", description="查看你的漁獲")
async def fish_back(interaction: discord.Interaction):
    if not os.path.exists('fishiback.yml'):
        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump({}, file)

    with open('fishiback.yml', 'r', encoding='utf-8') as file:
        fishing_data = yaml.safe_load(file)

    if fishing_data is None:
        fishing_data = {}

    user_id = str(interaction.user.id)

    if user_id in fishing_data and fishing_data[user_id]['caught_fish']:
        caught_fish = fishing_data[user_id]['caught_fish']
        
        fish_list = "\n".join([f"| **{fish['name']}** | {fish['rarity']} | {fish['size']} 公斤 |" for fish in caught_fish])
        
        header = "| 魚名 | 稀有度 | 重量 |\n| --- | --- | --- |"
        
        message = f"🎣 **你的漁獲列表**:\n{header}\n{fish_list}"
        
        await interaction.response.send_message(message, ephemeral=True)
    else:
        await interaction.response.send_message("❌ 你還沒有捕到任何魚！", ephemeral=True)

class CandyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="搜集糖果", style=discord.ButtonStyle.green)
    async def collect_candy(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if user_id not in candy_collection:
            candy_collection[user_id] = 0
        
        candies_gained = random.randint(1, 5)
        candy_collection[user_id] += candies_gained
        
        save_data(candy_collection)
        
        await interaction.response.send_message(f"你搜集到了 {candies_gained} 顆糖果！你現在總共有 {candy_collection[user_id]} 顆糖果。", ephemeral=True)

@bot.tree.command(name="start_candy_event", description="開始糖果搜集活動")
async def start_candy_event(interaction: discord.Interaction):
    view = CandyButton()
    await interaction.response.send_message("點擊按鈕來搜集糖果吧！", view=view)

@bot.tree.command(name="candyrank", description="顯示糖果排行榜")
async def candyrank(interaction: discord.Interaction):
    if not candy_collection:
        await interaction.response.send_message("目前還沒有人搜集糖果！")
        return

    sorted_collection = sorted(candy_collection.items(), key=lambda item: item[1], reverse=True)
    
    rank_emoji = ["🥇", "🥈", "🥉"]
    leaderboard = ""
    
    for idx, (user_id, candies) in enumerate(sorted_collection):
        if idx < 3:
            emoji = rank_emoji[idx]
        else:
            emoji = f"🏅 {idx+1}位"
        
        leaderboard += f"{emoji} <@{user_id}>: {candies} 顆糖果\n"
    
    embed = discord.Embed(
        title="🎃 糖果搜集排行榜 🍬",
        description=leaderboard,
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed)

class TrickOrTreatSelect(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(TrickOrTreatDropdown(options))

class TrickOrTreatDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="選擇一個成員進行 Trick or Treat", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_user = self.values[0]
        outcome = random.choice(["Trick", "Treat"])
        if outcome == "Treat":
            candies = random.randint(1, 10)
            candy_collection[interaction.user.id] = candy_collection.get(interaction.user.id, 0) + candies
            await interaction.response.send_message(f"你向 <@{selected_user}> 進行了 Trick or Treat！你獲得了 {candies} 顆糖果！")
        else:
            loss = random.randint(1, 5)
            candy_collection[interaction.user.id] = max(0, candy_collection.get(interaction.user.id, 0) - loss)
            await interaction.response.send_message(f"你向 <@{selected_user}> 進行了 Trick or Treat，但被惡作劇了！你損失了 {loss} 顆糖果。")

@bot.tree.command(name="start_treat_event", description="開始 Trick or Treat 活動")
async def start_treat_event(interaction: discord.Interaction):
    options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in interaction.guild.members if not member.bot]
    view = TrickOrTreatSelect(options)
    await interaction.response.send_message("選擇一個成員進行 Trick or Treat！", view=view)

bot.run(TOKEN)


