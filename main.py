import nextcord
from nextcord import app_commands
from nextcord.ext import commands
import os

# ตั้งค่า Intents
intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True 

# เปลี่ยนมาใช้ client แทน bot เพื่อรองรับ Slash Commands ได้ดีขึ้น
client = commands.Bot(command_prefix='/', intents=intents)

BotSever1 = 1204647300870311986  
BotSever2 = 1468565605836918846  

@client.event
async def on_ready():
    # ซิงค์คำสั่งให้แสดงบน Discord
    await client.tree.sync(guild=nextcord.Object(id=BotSever1))
    print(f'Logged in as {client.user}')
    
    guild = client.get_guild(BotSever1)
    if guild:
        vc_channel = nextcord.utils.get(guild.voice_channels, id=BotSever2)
        if vc_channel and not guild.voice_client:
            await vc_channel.connect(self_deaf=True)

# --- คำสั่ง Slash Command สำหรับเปิด/ปิด ---

@client.slash_command(name="off", description="ให้บอทออกจากห้องเสียง", guild_ids=[BotSever1])
async def bot_off(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ ออกจากห้องเสียงแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ", ephemeral=True)

@client.slash_command(name="on", description="ให้บอทเข้าห้องเสียง", guild_ids=[BotSever1])
async def bot_on(interaction: nextcord.Interaction):
    vc_channel = nextcord.utils.get(interaction.guild.voice_channels, id=BotSever2)
    if vc_channel:
        if not interaction.guild.voice_client:
            await vc_channel.connect(self_deaf=True)
            await interaction.response.send_message("✅ เข้าห้องเสียงแล้วครับ")
        else:
            await interaction.response.send_message("⚠️ บอทอยู่ในห้องเสียงอยู่แล้วครับ", ephemeral=True)
    else:
        await interaction.response.send_message("❌ ไม่พบช่องเสียงที่ระบุไว้ครับ", ephemeral=True)

# ----------------------------------------

client.run("ใส่_TOKEN_ของคุณที่นี่")
