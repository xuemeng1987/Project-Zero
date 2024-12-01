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
import yaml
import psutil
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from urllib.parse import urlparse

laod_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_MAIN2_BOT")
AUTHOR_ID = int(os.getenv('AUTHOR_ID'))

error_logger = logging.getLogger('discord')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(filename='error.log', encoding='utf-8', mode='w')
error_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
error_logger.addHandler(error_handler)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.message_content = True
last_activity_time = time.time()
intents.messages = True
participants = []

bot = commands.Bot(command_prefix='!', intents=intents)

user_balance = {}

def save_balance(data):
    with open('balance.yml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

def load_balance():
    if os.path.exists('balance.yml'):
        try:
            with open('balance.yml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print("Error loading balance.yml:", e)
            with open('balance.yml', 'r', encoding='utf-8') as f:
                print("Problematic file contents:")
                print(f.read())
    return {}

user_balance = load_balance()

# 機器人On_ready事件裝飾器
@bot.event
async def on_ready():
    print(f'已登入 {bot.user.name}')
    
    await bot.change_presence(
        status=discord.Status.idle, # 在綫狀態 閑置
        activity=discord.Activity(type=discord.ActivityType.playing, name='Blue Archive') # 游戲狀態 正在玩 “蔚藍檔案”
    )
    
    try:
        synced = await bot.tree.sync()
        print(f'成功同步 {len(synced)} 个命令')
    except Exception as e:
        print(f'同步命令时出错: {e}')
    
    last_activity_time = time.time() # 待機時間

# 指令 關閉機器人(綁定DiscordID)
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

# 指令 重啓機器人(綁定DiscordID)
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

# 指令 獲取最後的活動時間
@bot.tree.command(name="time", description="获取最后活动时间")
async def time_command(interaction: discord.Interaction):
    global last_activity_time
    current_time = time.time()
    idle_seconds = current_time - last_activity_time
    idle_minutes = idle_seconds / 60
    idle_hours = idle_seconds / 3600
    idle_days = idle_seconds / 86400
    if idle_days >= 1:
        await interaction.response.send_message(f'机器人上次活动时间是 {idle_days:.2f} 天前。')
    elif idle_hours >= 1:
        await interaction.response.send_message(f'机器人上次活动时间是 {idle_hours:.2f} 小时前。')
    else:
        await interaction.response.send_message(f'机器人上次活动时间是 {idle_minutes:.2f} 分钟前。')

# 指令 系統資源使用狀態(需要管理員權限)
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

# 釣魚系統 指令 和文件加載
with open('fishi.yml', 'r', encoding='utf-8') as file:
    fish_data = yaml.safe_load(file)

with open('fishi_shop.yml', 'r', encoding='utf-8') as file:
    shop_data = yaml.safe_load(file)

cooldowns = {}

class ShopView(discord.ui.View):
    def __init__(self, user_id, fish_list, guild_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.fish_list = fish_list
        self.guild_id = guild_id

        self.add_item(discord.ui.Button(
            label="出售漁獲",
            style=discord.ButtonStyle.secondary,
            custom_id="sell_fish"
        ))
        self.children[-1].callback = self.show_sell_fish

        self.add_item(discord.ui.Button(
            label="購買漁具",
            style=discord.ButtonStyle.primary,
            custom_id="buy_gear"
        ))
        self.children[-1].callback = self.show_gear_shop

    async def show_sell_fish(self, interaction: discord.Interaction):
        if not self.fish_list:
            await interaction.response.send_message("> 🎣 **你沒有漁獲可以出售。**", ephemeral=True)
            return

        await interaction.response.edit_message(
            content="> 🎣 **請選擇並出售你的漁獲：**",
            view=SellFishView(self.user_id, self.fish_list, self.guild_id)
        )

    async def show_gear_shop(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="> 🛠️ **歡迎來到漁具購買商店：**",
            view=GearShopView(self.user_id, self.guild_id)
        )

class SellFishView(discord.ui.View):
    BASE_PRICES = {
        'common': 50,
        'uncommon': 120,
        'rare': 140,
        'legendary': 1000,
        'deify': 4200,
        'unknown': 2000
    }

    def __init__(self, user_id, fish_list, guild_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.fish_list = fish_list[:25]
        self.guild_id = guild_id

        self.update_fish_menu()

    def update_fish_menu(self):
        """動態生成選擇菜單並添加到視圖"""
        if not self.fish_list:
            self.add_item(discord.ui.Button(
                label="無魚可售",
                style=discord.ButtonStyle.gray,
                disabled=True
            ))
            return

        options = [
            discord.SelectOption(
                label=f"{fish['name']} - 大小: {fish['size']:.2f} 公斤",
                description=f"估價: {self.calculate_fish_value(fish)} 幽靈幣",
                value=str(index)
            )
            for index, fish in enumerate(self.fish_list)
        ]

        select = discord.ui.Select(
            placeholder="選擇你想出售的魚",
            options=options,
            custom_id="fish_select"
        )
        select.callback = self.select_fish_to_sell
        self.add_item(select)

    def calculate_fish_value(self, fish):
        """計算魚的價值"""
        base_value = self.BASE_PRICES.get(fish['rarity'], 50)
        return int(base_value * fish['size'])

    async def select_fish_to_sell(self, interaction: discord.Interaction):
        selected_fish_index = int(interaction.data['values'][0])
        selected_fish = self.fish_list[selected_fish_index]
        await interaction.response.edit_message(
            content=f"> 🎣 **你選擇了出售: {selected_fish['name']} ({selected_fish['size']:.2f} 公斤)**",
            view=ConfirmSellView(self.user_id, selected_fish, self.fish_list, self.guild_id)
        )

class ConfirmSellView(discord.ui.View):
    def __init__(self, user_id, selected_fish, fish_list, guild_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.selected_fish = selected_fish
        self.fish_list = fish_list
        self.guild_id = guild_id

    def calculate_fish_value(self, fish):
        """計算魚的價值"""
        base_value = SellFishView.BASE_PRICES.get(fish['rarity'], 50)
        return int(base_value * fish['size'])

    @discord.ui.button(label="確認出售", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        fish_value = self.calculate_fish_value(self.selected_fish)

        try:
            with open('fishiback.yml', 'r', encoding='utf-8') as file:
                fish_back = yaml.safe_load(file) or {}
        except FileNotFoundError:
            fish_back = {}

        user_data = fish_back.get(self.user_id, {'coins': 0, 'caught_fish': []})
        user_data['coins'] = user_data.get('coins', 0) + fish_value
        user_data['caught_fish'] = [
            fish for fish in self.fish_list if fish != self.selected_fish
        ]
        fish_back[self.user_id] = user_data

        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump(fish_back, file)

        updated_fish_list = user_data['caught_fish']
        await interaction.response.edit_message(
            content=f"> 🎣 **成功出售 {self.selected_fish['name']}，獲得 {fish_value} 幽靈幣！**",
            view=SellFishView(self.user_id, updated_fish_list, self.guild_id)
        )

    @discord.ui.button(label="取消", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="> 🎣 **請選擇並出售你的漁獲：**",
            view=SellFishView(self.user_id, self.fish_list, self.guild_id)
        )

class GearShopView(discord.ui.View):
    def __init__(self, user_id, guild_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.guild_id = guild_id

        with open('fishi_shop.yml', 'r', encoding='utf-8') as file:
            shop_data = yaml.safe_load(file)

        self.rods = shop_data.get("rods", [])

        buy_rod_button = discord.ui.Button(
            label="購買釣竿",
            style=discord.ButtonStyle.primary,
            custom_id="buy_rod"
        )
        buy_rod_button.callback = self.buy_rod_menu
        self.add_item(buy_rod_button)

    async def buy_rod_menu(self, interaction: discord.Interaction):
        if not self.rods:
            await interaction.response.send_message("商店目前沒有魚竿可供購買！", ephemeral=True)
            return

        options = [
            discord.SelectOption(
                label=rod['name'], 
                description=f"價格: {rod['price']} 幽靈幣", 
                value=rod['name']
            )
            for rod in self.rods
        ]

        select = discord.ui.Select(
            placeholder="選擇要購買的釣竿",
            options=options,
            custom_id="rod_select"
        )
        select.callback = lambda inter: self.buy_rod(inter)

        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message("請選擇你想購買的釣竿：", view=view, ephemeral=True)

@bot.tree.command(name="fish_shop", description="查看釣魚商店並購買釣竿")
async def fish_shop(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)

    try:
        with open('fishiback.yml', 'r', encoding='utf-8') as file:
            fish_back = yaml.safe_load(file) or {}
    except FileNotFoundError:
        fish_back = {}

    if user_id not in fish_back:
        fish_back[user_id] = {'caught_fish': []}
        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump(fish_back, file)

    user_fish_list = fish_back[user_id]['caught_fish']

    await interaction.response.send_message(
        "> 🎣 歡迎來到釣魚商店！請選擇出售漁獲或購買漁具：",
        view=ShopView(user_id, user_fish_list, guild_id)
    )

def get_cooldown(user_rod):
    """根據魚竿計算冷卻時間"""
    cooldown_base = 5
    cooldown_reduction = {
        "普通釣竿": 1.0,
        "高級釣竿": 0.8,
        "傳說釣竿": 0.6,
    }
    multiplier = cooldown_reduction.get(user_rod, 1.0)
    return cooldown_base * multiplier

def catch_fish(user_rod):
    rarity_multiplier = {
        "普通釣竿": 1.0,
        "高級釣竿": 1.2,
        "傳說釣竿": 1.5,
    }
    multiplier = rarity_multiplier.get(user_rod, 1.0)

class FishView(discord.ui.View):
    def __init__(self, fish, user_id, rod):
        super().__init__(timeout=None)
        self.fish = fish
        self.user_id = user_id
        self.rod = rod

    @discord.ui.button(label="保存漁獲", style=discord.ButtonStyle.primary)
    async def save_fish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("這不是你的魚竿，請使用 `/fish` 來開始你的釣魚。", ephemeral=True)
            return

        if not os.path.exists('fishiback.yml'):
            with open('fishiback.yml', 'w', encoding='utf-8') as file:
                yaml.dump({}, file)

        with open('fishiback.yml', 'r', encoding='utf-8') as file:
            fish_back = yaml.safe_load(file) or {}

        if self.user_id not in fish_back:
            fish_back[self.user_id] = {'balance': 0, 'caught_fish': []}

        user_data = fish_back[self.user_id]
        user_data['caught_fish'].append(self.fish)

        with open('fishiback.yml', 'w', encoding='utf-8') as file:
            yaml.dump(fish_back, file)

        await interaction.response.edit_message(content=f"✅ 你保存了 {self.fish['name']} ({self.fish['size']} 公斤) 到你的漁獲列表中！", view=None)

    @discord.ui.button(label="再釣一次", style=discord.ButtonStyle.secondary)
    async def fish_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("這不是你的魚竿，請使用 `/fish` 來開始你的釣魚。", ephemeral=True)
            return

        cooldown_time = get_cooldown(self.rod)
        if self.user_id in cooldowns and time.time() - cooldowns[self.user_id] < cooldown_time:
            remaining_time = cooldown_time - (time.time() - cooldowns[self.user_id])
            await interaction.response.send_message(f"⏳ 你需要等待 {remaining_time:.1f} 秒後才能再次釣魚。", ephemeral=True)
            return

        cooldowns[self.user_id] = time.time()

        new_fish = catch_fish(self.rod)
        self.fish = new_fish
        await interaction.response.edit_message(
            content=f"🎣 你捕到了一條 {new_fish['rarity']} 的 {new_fish['name']}！它的大小是 {new_fish['size']} 公斤！",
            view=FishView(new_fish, self.user_id, self.rod)
        )

@bot.tree.command(name="fish", description="進行一次釣魚")
async def fish(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if not os.path.exists('user_rod.yml'):
        with open('user_rod.yml', 'w', encoding='utf-8') as file:
            yaml.dump({}, file)

    with open('user_rod.yml', 'r', encoding='utf-8') as file:
        user_rods = yaml.safe_load(file) or {}

    user_data = user_rods.get(user_id, {"current_rod": "普通釣竿"})
    current_rod = user_data.get("current_rod", "普通釣竿")

    cooldown_time = get_cooldown(current_rod)
    if user_id in cooldowns and time.time() - cooldowns[user_id] < cooldown_time:
        remaining_time = cooldown_time - (time.time() - cooldowns[user_id])
        await interaction.response.send_message(f"⏳ 你需要等待 {remaining_time:.1f} 秒後才能再次釣魚。", ephemeral=True)
        return

    cooldowns[user_id] = time.time()

    fish_caught = catch_fish(current_rod)
    await interaction.response.send_message(
        f"🎣 你捕到了一條 {fish_caught['rarity']} 的 {fish_caught['name']}！它的大小是 {fish_caught['size']} 公斤！",
        view=FishView(fish_caught, user_id, current_rod)
    )

class RodView(discord.ui.View):
    def __init__(self, user_id, available_rods, current_rod):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.available_rods = available_rods
        self.current_rod = current_rod
        
        select = discord.ui.Select(
            placeholder=f"🎣 目前釣竿: {current_rod}",
            options=[
                discord.SelectOption(
                    label=rod["name"],
                    value=rod["name"],
                    description=rod.get("description", f"切換到 {rod['name']}"),
                    emoji=rod.get("emoji", "🎣")
                )
                for rod in available_rods
            ],
            custom_id="rod_select"
        )
        select.callback = self.switch_rod
        self.add_item(select)

    async def switch_rod(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("🚫 這不是你的設定菜單，請使用 `/fish_rod` 查看你的釣竿。", ephemeral=True)
            return
        
        selected_rod = interaction.data['values'][0]
        self.update_user_rod(str(self.user_id), selected_rod)
        await interaction.response.edit_message(
            content=f"✅ 你已切換到: **{selected_rod}**",
            view=RodView(self.user_id, self.available_rods, selected_rod)
        )

    @staticmethod
    def update_user_rod(user_id, new_rod):
        """更新用戶的釣竿設定到文件"""
        try:
            with open('user_rod.yml', 'r', encoding='utf-8') as file:
                user_rods = yaml.safe_load(file)
        except FileNotFoundError:
            user_rods = {}
        if user_id not in user_rods:
            user_rods[user_id] = {"rods": [{"name": "普通釣竿", "description": "適合新手的釣竿"}], "current_rod": "普通釣竿"}
        user_rods[user_id]["current_rod"] = new_rod
        with open('user_rod.yml', 'w', encoding='utf-8') as file:
            yaml.dump(user_rods, file)

@bot.tree.command(name="fish_rod", description="查看並切換你的釣魚竿")
async def fish_rod(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if not os.path.exists('user_rod.yml'):
        with open('user_rod.yml', 'w', encoding='utf-8') as file:
            yaml.dump({}, file)
    
    with open('user_rod.yml', 'r', encoding='utf-8') as file:
        try:
            user_rods = yaml.safe_load(file) or {}
        except yaml.YAMLError:
            user_rods = {}
    
    if user_id not in user_rods or not isinstance(user_rods[user_id], dict):
        user_rods[user_id] = {
            "rods": [{"name": "普通釣竿", "description": "適合新手的釣竿"}],
            "current_rod": "普通釣竿"
        }
    with open('user_rod.yml', 'w', encoding='utf-8') as file:
        yaml.dump(user_rods, file)
    
    user_data = user_rods[user_id]
    available_rods = user_data["rods"]
    current_rod = user_data["current_rod"]
    
    await interaction.response.send_message(
        f"🎣 你現在使用的釣竿是: **{current_rod}**\n"
        f"⬇️ 從下方選單選擇以切換釣竿！",
        view=RodView(user_id, available_rods, current_rod)
    )

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
        fish_list = "\n".join(
            [f"| **{fish['name']}** | {fish['rarity']} | {fish['size']} 公斤 |" for fish in caught_fish]
        )
        header = "| 魚名 | 稀有度 | 重量 |\n| --- | --- | --- |"
        message = f"> 🎣 **你的漁獲列表**:\n> {header}\n>>> {fish_list}"
        
        await interaction.response.send_message(message, ephemeral=False)
    else:
        await interaction.response.send_message("❌ 你還沒有捕到任何魚！", ephemeral=True)

# 指令 賬戶餘額
@bot.tree.command(name="balance", description="查询用户余额")
async def balance(interaction: discord.Interaction):
    global user_balance
    user_balance = load_balance()
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    if guild_id not in user_balance:
        user_balance[guild_id] = {}
    balance = user_balance[guild_id].get(user_id, 0)
    await interaction.response.send_message(f'{interaction.user.name} 在此群組的幽靈幣餘額: {balance}')

# 指令 群組最富有的用戶
@bot.tree.command(name="balance_top", description="查看幽靈幣排行榜")
async def balance_top(interaction: discord.Interaction):
    try:
        with open('balance.yml', 'r', encoding='utf-8') as file:
            balance_data = yaml.safe_load(file)
        guild_id = str(interaction.guild.id)
        if not balance_data or guild_id not in balance_data:
            await interaction.response.send_message("目前沒有排行榜數據。", ephemeral=True)
            return
        guild_balances = balance_data[guild_id]
        sorted_balances = sorted(guild_balances.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []
        for index, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
            member = interaction.guild.get_member(int(user_id))
            username = member.display_name if member else f"用戶 {user_id}"
            leaderboard.append(f"**#{index}** - {username}: {balance} 幽靈幣")
        leaderboard_message = "\n".join(leaderboard)
        await interaction.response.send_message(f"🏆 **幽靈幣排行榜** 🏆\n\n{leaderboard_message}")
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {e}")
        await interaction.response.send_message("找不到 balance.yml 文件。", ephemeral=True)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await interaction.response.send_message(f"發生錯誤：{e}", ephemeral=True)

bot.run(TOKEN)
