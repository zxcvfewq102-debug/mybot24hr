import nextcord
from nextcord.ext import commands
import os
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบเปิดพอร์ต 24 ชม. ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running 24/7!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- ตั้งค่าบอท ---
load_dotenv()
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

# --- ตั้งค่า yt-dlp พร้อม Cookies ---
ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'webm', 'preferredquality': '192'}],
}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user}')

# --- ระบบตอบกลับอัตโนมัติ (Auto-response) ---
@bot.event
async def on_message(message):
    # ป้องกันไม่ให้บอทตอบตัวเอง
    if message.author == bot.user:
        return

    # ถ้าเจอคำที่กำหนดให้บอทตอบกลับ
    if "สวัสดี" in message.content:
        await message.channel.send(f"สวัสดีครับคุณ {message.author.mention} มีอะไรให้ผมรับใช้ไหมครับ?")
    
    if "ขอโปรหน่อย" in message.content:
        await message.channel.send("หาเองดีไอ้คาวยไอ้โง่")

    # สำคัญมาก: ต้องมีบรรทัดนี้เพื่อให้บอทอ่านคำสั่ง slash command อื่นๆ ได้ด้วย
    await bot.process_commands(message)

# --- Slash Commands ---

@bot.slash_command(name="hello", description="ทักทายบอท")
async def hello(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"สวัสดีครับ {interaction.user.mention}! ผมพร้อมใช้งานแล้วครับ 🤖")

@bot.slash_command(name="ask", description="ถามคำถามบอท")
async def ask(interaction: nextcord.Interaction, question: str):
    answers = {
        "บอททำอะไรได้บ้าง": "ฉันสามารถเล่นเพลง สั่งหยุด และทักทายคุณได้ครับ!",
        "ใครสร้างคุณ": "ฉันถูกสร้างขึ้นโดยคุณเจ้าของบอทคนเก่งครับ",
        "เวลาตอนนี้กี่โมง": "ขออภัยครับ ฉันเป็นบอทเพลง ยังดูเวลาให้ไม่ได้ครับ"
    }
    response = answers.get(question, "ขออภัยครับ ผมไม่เข้าใจคำถามนี้ หรือไม่มีข้อมูลในระบบครับ")
    await interaction.response.send_message(f"❓ คำถาม: {question}\n🤖 คำตอบ: {response}")

@bot.slash_command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: nextcord.Interaction, url: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ ต้องอยู่ในห้องเสียงก่อนครับ")
    
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    await interaction.response.defer() 
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info.get('url')
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            interaction.guild.voice_client.play(source)
            await interaction.followup.send(f"🎵 กำลังเล่น: {info['title']}")
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.slash_command(name="stop", description="หยุดเพลง")
async def stop(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ หยุดเล่นเพลงแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

@bot.slash_command(name="leave", description="ให้บอทออกจากห้อง")
async def leave(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("📤 ออกจากห้องแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
