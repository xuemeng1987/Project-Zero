import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import random
import json
from datetime import datetime, timedelta

TOKEN = 'token'
ALLOWED_AUTHOR_ID = 699869229712670780

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

user_balance = {}
rpg_data = {}

def save_balance(data):
    with open('balance.json', 'w') as f:
        json.dump(data, f)

def load_balance():
    if os.path.exists('balance.json'):
        with open('balance.json', 'r') as f:
            return json.load(f)
    return {}

def save_rpg_data(data):
    with open('rpg_data.json', 'w') as f:
        json.dump(data, f)

def load_rpg_data():
    if os.path.exists('rpg_data.json'):
        with open('rpg_data.json', 'r') as f:
            return json.load(f)
    return {}

user_balance = load_balance()
rpg_data = load_rpg_data()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()

@bot.tree.command(name="balance", description="查询用户余额")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = user_balance.get(user_id, 0)
    await interaction.response.send_message(f'{interaction.user.name} 的比特幣余额: {balance}')

@bot.tree.command(name="work", description="赚取比特幣")
async def work(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    amount = random.randint(5, 20)
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

@bot.tree.command(name="rpg", description="初始化 RPG 用户数据")
async def rpg(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in rpg_data:
        await interaction.response.send_message("你已经在 RPG 游戏中！")
    else:
        rpg_data[user_id] = {
            "level": 1,
            "exp": 0,
            "money": 100,
            "items": []
        }
        save_rpg_data(rpg_data)
        await interaction.response.send_message("你已经开始了 RPG 游戏！")

@bot.tree.command(name="rpg_shop", description="显示 RPG 商店")
async def rpg_shop(interaction: discord.Interaction):
    shop_items = {
        "剑": 50,
        "盾": 30,
        "药水": 20
    }
    shop_text = "商店物品及价格:\n"
    for item, price in shop_items.items():
        shop_text += f"{item}: {price} 比特幣\n"
    await interaction.response.send_message(shop_text)

@bot.tree.command(name="rpg_adventure", description="前往地下城冒险")
async def rpg_adventure(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in rpg_data:
        await interaction.response.send_message("你尚未开始 RPG 游戏！使用 /rpg 开始游戏。")
        return

    result = random.choice(["胜利", "失败"])
    if result == "胜利":
        reward = random.randint(10, 50)
        rpg_data[user_id]["money"] += reward
        save_rpg_data(rpg_data)
        await interaction.response.send_message(f"你在冒险中胜利了！获得了 {reward} 比特幣。")
    else:
        await interaction.response.send_message("你在冒险中失败了。下次好运！")

@bot.tree.command(name="rpg_info", description="显示 RPG 用户信息")
async def rpg_info(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in rpg_data:
        await interaction.response.send_message("你尚未开始 RPG 游戏！使用 /rpg 开始游戏。")
        return

    user_data = rpg_data[user_id]
    info_text = f"""
    角色等级: {user_data['level']}
    经验值: {user_data['exp']}
    比特币: {user_data['money']}
    背包物品: {', '.join(user_data['items'])}
    """
    await interaction.response.send_message(info_text)

@bot.tree.command(name="rpg_profile", description="显示 RPG 用户个人主页")
async def rpg_profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in rpg_data:
        await interaction.response.send_message("你尚未开始 RPG 游戏！使用 /rpg 开始游戏。")
        return

    user_data = rpg_data[user_id]
    profile_text = f"""
    **角色信息**
    等级: {user_data['level']}
    经验: {user_data['exp']}
    比特币: {user_data['money']}
    背包物品: {', '.join(user_data['items'])}
    """
    await interaction.response.send_message(profile_text)

@bot.tree.command(name="addmoney", description="给用户增加比特币（管理员专用）")
async def addmoney(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.id == ALLOWED_AUTHOR_ID:
        recipient_id = str(member.id)
        user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
        save_balance(user_balance)
        await interaction.response.send_message(f'给 {member.name} 增加了 {amount} 比特币。')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="shutdown", description="关闭机器人")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == ALLOWED_AUTHOR_ID:
        await interaction.response.send_message("关闭中...")
        await bot.close()
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="restart", description="重启机器人")
async def restart(interaction: discord.Interaction):
    if interaction.user.id == ALLOWED_AUTHOR_ID:
        await interaction.response.send_message("重启中...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="ban", description="封禁用户")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f'{member} 已被封禁.')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="kick", description="踢出用户")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f'{member} 已被踢出.')
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="clear", description="清除消息")
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.manage_messages:
        if amount <= 0:
            await interaction.response.send_message("请输入一个大于 0 的数字。")
            return
        if amount > 100:
            await interaction.response.send_message("无法一次性删除超过 100 条消息。")
            return

        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted = 0

        async for message in interaction.channel.history(limit=amount):
            if message.created_at >= cutoff_date:
                await message.delete()
                deleted += 1

        await interaction.response.send_message(f'已删除 {deleted} 条消息。', delete_after=5)
    else:
        await interaction.response.send_message("你没有权限执行此操作。")

@bot.tree.command(name="help", description="显示所有可用指令")
async def help(interaction: discord.Interaction):
    help_text = """
    /balance - 查询用户余额
    /work - 赚取比特币
    /pay - 转账给其他用户
    /rpg - 初始化 RPG 用户数据
    /rpg_shop - 显示 RPG 商店
    /rpg_adventure - 前往地下城冒险
    /rpg_info - 显示 RPG 用户信息
    /rpg_profile - 显示 RPG 用户个人主页
    /addmoney - 给用户增加比特币（管理员權限）
    /ban - 封禁用户 (管理員權限)
    /kick - 踢出用户 (管理員權限)
    /clear - 清除消息 (管理員權限)
    /shutdown - 關閉機器人 (製作者beta測試使用指令)
    /restart - 重啓機器人 (製作者beta測試使用指令)
    more commands is comeing soon...
    """
    await interaction.response.send_message(help_text)

def log_error(message):
    with open('log.json', 'a') as log_file:
        log_file.write(f'{datetime.now()}: {message}\n')

bot.run(TOKEN)
