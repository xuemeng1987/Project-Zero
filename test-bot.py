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

@bot.tree.command(name="rpg_start", description="初始化角色数据")
async def rpg_start(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = {
        'lv': 1,
        'exp': 0,
        'hp': 20,
        'mp': 20,
        'stamina': 10
    }
    
    if not os.path.exists('rpg-data'):
        os.makedirs('rpg-data')
    
    with open(f'rpg-data/{user_id}.yml', 'w') as file:
        yaml.dump(data, file)
    
    await interaction.response.send_message("角色已初始化，开始你的冒险吧！")

@bot.tree.command(name="rpg_backpack", description="开启背包")
async def rpg_backpack(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    try:
        with open(f'backpack/{user_id}.yml', 'r') as file:
            backpack = yaml.safe_load(file)
        
        options = [SelectOption(label=item, description=f"数量: {backpack[item]['quantity']}")
                   for item in backpack]

        select = Select(placeholder="选择一个物品查看详情", options=options)

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
        await interaction.response.send_message(f"你购买了 {quantity} 个 {self.item['name']}，共花费 {total_cost} BTC")

@bot.tree.command(name="rpg_shop", description="前往商店")
async def rpg_shop(interaction: discord.Interaction):
    with open('shop_item.yml', 'r', encoding='utf-8') as file:
        shop_items = yaml.safe_load(file)
    
    view = View()
    view.add_item(ShopSelect(shop_items))
    
    await interaction.response.send_message("欢迎来到商店，请选择你要访问的店铺：", view=view)

@bot.tree.command(name="rpg_adventure", description="開啟冒險")
async def rpg_adventure(interaction: discord.Interaction):
    try:
        with open('dungeon.yml', 'r') as dungeon_file:
            dungeon_data = yaml.safe_load(dungeon_file)
        with open('monster_item.yml', 'r') as monster_item_file:
            monster_items = yaml.safe_load(monster_item_file)
        with open('monster.yml', 'r') as monster_file:
            monsters = yaml.safe_load(monster_file)
        
        await interaction.response.send_message("冒險開始！")
    
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

        logging.error(f"文件丟失: {missing_file}，請檢查源代碼中相關文件的存在性。")

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

bot.run(TOKEN)
