import discord
from discord import app_commands
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True # จำเป็นสำหรับการระบุตัวสมาชิก

client = commands.Bot(command_prefix="!", intents=intents)

# ตัวแปรสำหรับเกม
game_data = {} # ใช้ dictionary เพื่อรองรับหลายห้อง/หลายเกม

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"{client.user} พร้อมใช้งานแล้ว!")

@client.tree.command(name="xo", description="เริ่มเกม XO")
async def xo(interaction: discord.Interaction, p1: discord.Member, p2: discord.Member):
    # สร้างข้อมูลเกมสำหรับ server นี้
    game_data[interaction.guild_id] = {
        "board": [":white_large_square:"] * 9,
        "p1": p1,
        "p2": p2,
        "turn": random.choice([p1, p2]),
        "count": 0,
        "gameOver": False
    }
    
    data = game_data[interaction.guild_id]
    board_str = "\n".join(["".join(data["board"][i:i+3]) for i in range(0, 9, 3)])
    
    await interaction.response.send_message(f"เริ่มเกม! {p1.mention} vs {p2.mention}\n{board_str}\nตาของ {data['turn'].mention}")

@client.tree.command(name="วาง", description="วาง X หรือ O (ใส่เลข 1-9)")
async def place(interaction: discord.Interaction, pos: int):
    if interaction.guild_id not in game_data or game_data[interaction.guild_id]["gameOver"]:
        await interaction.response.send_message("ยังไม่มีเกมเริ่ม หรือเกมจบไปแล้ว! ใช้ /xo เพื่อเริ่มใหม่")
        return

    data = game_data[interaction.guild_id]
    
    if interaction.user != data["turn"]:
        await interaction.response.send_message("ไม่ใช่ตาของคุณ!")
        return
    
    if 1 <= pos <= 9 and data["board"][pos - 1] == ":white_large_square:":
        mark = ":regional_indicator_x:" if data["turn"] == data["p1"] else ":o2:"
        data["board"][pos - 1] = mark
        data["count"] += 1
        
        # เช็คชนะ
        winner = False
        wins = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        for w in wins:
            if data["board"][w[0]] == data["board"][w[1]] == data["board"][w[2]] == mark:
                winner = True
        
        board_str = "\n".join(["".join(data["board"][i:i+3]) for i in range(0, 9, 3)])
        
        if winner:
            data["gameOver"] = True
            await interaction.response.send_message(f"{interaction.user.mention} ชนะ!\n{board_str}")
        elif data["count"] >= 9:
            data["gameOver"] = True
            await interaction.response.send_message(f"เสมอ!\n{board_str}")
        else:
            data["turn"] = data["p2"] if data["turn"] == data["p1"] else data["p1"]
            await interaction.response.send_message(f"วางสำเร็จ!\n{board_str}\nตาของ {data['turn'].mention}")
    else:
        await interaction.response.send_message("ช่องไม่ว่างหรือใส่เลขผิด!")

# รันบอทโดยใช้ Token จากไฟล์ .env
client.run(os.getenv('DISCORD_TOKEN'))
