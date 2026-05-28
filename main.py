import nextcord
from nextcord.ext import commands
import os

# 1. ตั้งค่า Intents
intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

# 2. ตั้งค่า Bot
bot = commands.Bot(command_prefix='!', intents=intents)

BotSever1 = 1204647300870311986  # ID เซิร์ฟเวอร์
BotSever2 = 1468565605836918846  # ID ห้องเสียง

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        await bot.tree.sync(guild=nextcord.Object(id=BotSever1))
        print("✅ Slash commands synced")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# คำสั่ง /off: ให้บอทออกจากห้องเสียง
@bot.slash_command(name="off", description="ให้บอทออกจากห้องเสียง", guild_ids=[BotSever1])
async def bot_off(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ ออกจากห้องเสียงแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ", ephemeral=True)

# คำสั่ง /on: ให้บอทเข้าห้องเสียง
@bot.slash_command(name="on", description="ให้บอทเข้าห้องเสียง", guild_ids=[BotSever1])
async def bot_on(interaction: nextcord.Interaction):
    vc_channel = nextcord.utils.get(interaction.guild.voice_channels, id=BotSever2)
    if vc_channel:
        if not interaction.guild.voice_client:
            # 1. เชื่อมต่อเข้าห้องเสียง
            await vc_channel.connect()
            # 2. ตั้งค่า self_deaf แยกออกมาทีหลัง
            await interaction.guild.change_voice_state(channel=vc_channel, self_deaf=True)
            await interaction.response.send_message("✅ เข้าห้องเสียงแล้วครับ")
        else:
            await interaction.response.send_message("⚠️ บอทอยู่ในห้องเสียงอยู่แล้วครับ", ephemeral=True)
    else:
        await interaction.response.send_message("❌ ไม่พบช่องเสียงที่ระบุไว้ครับ", ephemeral=True)

# รันบอท
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ ERROR: กรุณาตั้งค่า DISCORD_TOKEN ใน Railway Variables")
