import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import yt_dlp
import asyncio
import os

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(help_command=None, intents=intents)

# ตั้งค่าระบบดึงเสียงจาก YouTube ให้มีประสิทธิภาพสูง
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'default_search': 'ytsearch'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    # สั่งอัปเดตคำสั่งสแลช (/) ไปยังทุกเซิร์ฟเวอร์
    await bot.sync_all_application_commands()
    print(f'🟢 บอทเพลงระบบ Slash Command ({bot.user.name}) ออนไลน์พร้อมใช้งานแล้ว!')

# 🎵 1. คำสั่ง /play (เปิดเพลง)
@bot.slash_command(name="play", description="สั่งเปิดเพลงด้วยชื่อเพลง หรือ วางลิงก์ YouTube")
async def play(
    interaction: Interaction, 
    search: str = SlashOption(description="พิมพ์ชื่อเพลง หรือ วางลิงก์ YouTube ที่นี่", required=True)
):
    await interaction.response.defer()

    # ตรวจสอบว่าผู้ใช้เข้าห้องเสียงหรือยัง
    if not interaction.user.voice:
        return await interaction.followup.send("❌ คุณต้องเข้าห้องเสียงก่อนสั่งเปิดเพลงครับ!")

    voice_channel = interaction.user.voice.channel

    # สั่งให้บอทเชื่อมต่อเข้าห้องเสียง
    if not interaction.guild.voice_client:
        await voice_channel.connect()
    
    guild_vc = interaction.guild.voice_client

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
        
        if 'entries' in data:
            video = data['entries'][0]
        else:
            video = data
            
        song_url = video['url']
        title = video['title']
    except Exception as e:
        return await interaction.followup.send(f"❌ เกิดข้อผิดพลาดในการค้นหาเพลง: {e}")

    # สั่งหยุดเพลงเก่าก่อนเล่นเพลงใหม่
    if guild_vc.is_playing():
        guild_vc.stop()
        
    # บน Hugging Face สามารถเรียกใช้คำว่า "ffmpeg" ตรงๆ ได้เลย
    audio_source = nextcord.FFmpegPCMAudio(song_url, executable="ffmpeg", **FFMPEG_OPTIONS)
    guild_vc.play(audio_source)
    
    await interaction.followup.send(f"🎵 **กำลังเปิดเพลง:** {title}")

# ⏭️ 2. คำสั่ง /skip (ข้ามเพลง)
@bot.slash_command(name="skip", description="ข้ามเพลงที่กำลังเล่นอยู่")
async def skip(interaction: Interaction):
    guild_vc = interaction.guild.voice_client
    if guild_vc and guild_vc.is_playing():
        guild_vc.stop()
        await interaction.response.send_message("⏭️ ข้ามเพลงเรียบร้อยครับ")
    else:
        await interaction.response.send_message("❌ ตอนนี้ไม่มีเพลงกำลังเล่นอยู่ครับ")

# 👋 3. คำสั่ง /stop (หยุดและออกจากห้อง)
@bot.slash_command(name="stop", description="หยุดเล่นเพลงและให้บอทออกจากห้องเสียง")
async def stop(interaction: Interaction):
    guild_vc = interaction.guild.voice_client
    if guild_vc:
        await guild_vc.disconnect()
        await interaction.response.send_message("👋 หยุดเล่นเพลงและออกจากห้องเสียงเรียบร้อยครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

# รันบอทด้วย Token ลับจากหน้า Settings
bot.run(os.getenv("DISCORD_TOKEN"))
