import nextcord
from nextcord.ext import commands
import os
import yt_dlp
import requests
import random
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบเปิดพอร์ต 24 ชม. ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running 24/7!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

load_dotenv()
intents = nextcord.Intents.all()
intents.message_content = True
bot = commands.Bot(intents=intents)

# ระบบคิวเพลง
queues = {}

# --- ใส่ Ydl_opts ตามที่คุณขอมา ---
ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt',
    'noplaylist': True,
}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

# --- ระบบตอบโต้แชท ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if "สวัสดี" in message.content: await message.channel.send(f"สวัสดีครับคุณ {message.author.mention} มีอะไรให้ผมรับใช้ไหมครับ?")
    if "ขอโปรหน่อย" in message.content: await message.channel.send(f"นี่ครับโปรของคุณ {message.author.mention} 🎁")
    await bot.process_commands(message)

# --- Slash Commands: สารพัดประโยชน์ ---
@bot.slash_command(name="hello", description="ทักทายบอท")
async def hello(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"สวัสดีครับ {interaction.user.mention}! ผมพร้อมใช้งานแล้วครับ 🤖")

@bot.slash_command(name="ping", description="เช็กความหน่วงบอท")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 ({round(bot.latency * 1000)}ms)")

@bot.slash_command(name="userinfo", description="ดูข้อมูลสมาชิก")
async def userinfo(interaction: nextcord.Interaction, member: nextcord.Member = None):
    member = member or interaction.user
    embed = nextcord.Embed(title=f"ข้อมูลของ {member.name}", color=nextcord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="วันที่เข้าเซิร์ฟเวอร์", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.slash_command(name="random", description="สุ่มเลข 1-100")
async def random_num(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"🎲 ผลการสุ่มคือ: {random.randint(1, 100)}")

@bot.slash_command(name="weather", description="เช็กสภาพอากาศ")
async def weather(interaction: nextcord.Interaction, city: str):
    api_key = "984cc187c35afb6f1b44d39de7fb191e" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=th"
    try:
        await interaction.response.defer()
        response = requests.get(url).json()
        if response.get("cod") != 200: return await interaction.followup.send("❌ ไม่พบเมืองนี้ครับ")
        await interaction.followup.send(f"🌤️ อากาศที่ {response['name']}: {response['weather'][0]['description']} อุณหภูมิ {response['main']['temp']}°C")
    except Exception as e: await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.slash_command(name="kick", description="เตะสมาชิกออกจากเซิร์ฟเวอร์")
async def kick(interaction: nextcord.Interaction, member: nextcord.Member, reason: str = "ไม่มีเหตุผล"):
    if not interaction.user.guild_permissions.kick_members: return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้งาน!")
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ เตะ {member.name} เรียบร้อยแล้ว")

# --- Slash Commands: เพลง (ระบบคิว) ---
@bot.slash_command(name="play", description="ค้นหาและเพิ่มเพลงเข้าคิว")
async def play(interaction: nextcord.Interaction, search: str):
    if not interaction.user.voice: return await interaction.response.send_message("❌ ต้องเข้าห้องเสียงก่อนครับ")
    await interaction.response.defer()
    if interaction.guild.id not in queues: queues[interaction.guild.id] = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        video = info['entries'][0] if 'entries' in info else info
        queues[interaction.guild.id].append(video)
        await interaction.followup.send(f"➕ เพิ่มเข้าคิว: {video['title']}")
        if not interaction.guild.voice_client: await interaction.user.voice.channel.connect()
        if not interaction.guild.voice_client.is_playing(): await play_next(interaction)

async def play_next(interaction):
    guild_id = interaction.guild.id
    if queues.get(guild_id):
        video = queues[guild_id].pop(0)
        source = await nextcord.FFmpegOpusAudio.from_probe(video['url'], **ffmpeg_options)
        interaction.guild.voice_client.play(source, after=lambda e: bot.loop.create_task(play_next(interaction)))
        await interaction.channel.send(f"🎵 กำลังเล่น: {video['title']}")
    else: await interaction.channel.send("✅ เล่นคิวจนหมดแล้วครับ")

@bot.slash_command(name="skip", description="ข้ามเพลงที่เล่นอยู่")
async def skip(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ ข้ามเพลงเรียบร้อย!")
    else: await interaction.response.send_message("❌ ไม่ได้เล่นเพลงอยู่ครับ")

@bot.slash_command(name="stop", description="หยุดเพลง")
async def stop(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ หยุดเล่นเพลงแล้วครับ")
    else: await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

@bot.slash_command(name="leave", description="บอทออกจากห้อง")
async def leave(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("📤 ออกจากห้องแล้วครับ")
    else: await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
