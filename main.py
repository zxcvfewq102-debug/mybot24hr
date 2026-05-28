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

BotSever1 = 1204647300870311986
BotSever2 = 1468565605836918846

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        # ซิงค์คำสั่ง Slash Command
        await bot.tree.sync(guild=nextcord.Object(id=BotSever1))
        print("✅ Slash commands synced")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    
    # บอทเข้าห้องเสียงอัตโนมัติเมื่อเริ่มระบบ
    guild = bot.get_guild(BotSever1)
    if guild:
        vc_channel = nextcord.utils.get(guild.voice_channels, id=BotSever2)
        if vc_channel and not guild.voice_client:
            try:
                await vc_channel.connect(self_deaf=True)
                print(f'✅ Connected to {vc_channel.name}')
            except Exception as e:
                print(f'❌ Error connecting to voice: {e}')

# 3. Slash Commands
@bot.slash_command(name="off", description="ให้บอทออกจากห้องเสียง", guild_ids=[BotSever1])
async def bot_off(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ ออกจากห้องเสียงแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ", ephemeral=True)

@bot.slash_command(name="on", description="ให้บอทเข้าห้องเสียง", guild_ids=[BotSever1])
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

# 4. การรันบอท (ดึง Token จาก Railway Variables)
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("❌ ERROR: DISCORD_TOKEN not found in environment variables!")
else:
    bot.run(token)
