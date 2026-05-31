import discord
import os
from discord.ext import commands
import asyncio
import yt_dlp
from aiohttp import web
import logging

# เปิดใช้งานการบันทึก Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # สร้างระบบคิวเพลงเก็บไว้ในตัวบอท
        self.queues = {} 

    async def setup_hook(self):
        # เปิด Web Server เพื่อรองรับระบบ Health Check ของ Railway บอทจะได้ไม่ดับ
        async def web_server():
            app = web.Application()
            app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
            runner = web.AppRunner(app)
            await runner.setup()
            port = int(os.getenv("PORT", 8080))
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            logger.info(f"Web server started on port {port} for Railway")

        self.loop.create_task(web_server())
        
        # Sync คำสั่งสแลช (Slash Commands)
        MY_GUILD_ID = discord.Object(id=1204647300870311986) 
        self.tree.copy_global_to(guild=MY_GUILD_ID)
        await self.tree.sync(guild=MY_GUILD_ID)
        print("Bot is ready and Commands Synced!")

bot = MusicBot()

# ตั้งค่า yt-dlp สำหรับดึงเสียงจาก YouTube
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# ฟังก์ชันจัดการเล่นเพลงถัดไปในคิวอัตโนมัติ
def play_next(ctx_or_interaction, guild_id):
    if guild_id in bot.queues_data and bot.queues_data[guild_id]:
        next_track = bot.queues_data[guild_id].pop(0)
        vc = ctx_or_interaction.guild.voice_client
        if vc and vc.is_connected():
            vc.play(discord.FFmpegPCMAudio(next_track['url'], **FFMPEG_OPTIONS), 
                    after=lambda e: play_next(ctx_or_interaction, guild_id))
            
            # ส่งข้อความแจ้งเตือนเพลงถัดไป
            coro = next_track['channel'].send(
                embed=discord.Embed(title="🎵 กำลังเล่นเพลงถัดไป", description=f"**{next_track['title']}**", color=discord.Color.green()),
                view=MusicControlView()
            )
            asyncio.run_coroutine_threadsafe(coro, bot.loop)

bot.queues_data = {}

class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⏸️/▶️", style=discord.ButtonStyle.blurple)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            if vc.is_playing():
                vc.pause()
                await interaction.response.send_message("หยุดเพลงชั่วคราว", ephemeral=True)
            elif vc.is_paused():
                vc.resume()
                await interaction.response.send_message("เล่นเพลงต่อ", ephemeral=True)
        else:
            await interaction.response.send_message("บอทไม่ได้อยู่ในห้องเสียง", ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            if interaction.guild.id in bot.queues_data:
                bot.queues_data[interaction.guild.id].clear()
            await vc.disconnect()
            await interaction.response.send_message("หยุดเพลงและออกจากห้องแชทแล้ว", ephemeral=True)

@bot.tree.command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("ต้องอยู่ในห้องเสียงก่อนครับ!", ephemeral=True)
    
    await interaction.response.defer()
    guild_id = interaction.guild.id

    if guild_id not in bot.queues_data:
        bot.queues_data[guild_id] = []

    # ค้นหาและดึงข้อมูลเพลง
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        
        track_info = {
            'url': data['url'],
            'title': data['title'],
            'channel': interaction.channel
        }
    except Exception as e:
        logger.error(f"Error extracting video: {e}")
        return await interaction.followup.send("เกิดข้อผิดพลาดในการดึงข้อมูลเพลง")

    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()

    if vc.is_playing() or vc.is_paused():
        bot.queues_data[guild_id].append(track_info)
        embed = discord.Embed(
            title="⏳ เพิ่มเข้าคิวแล้ว", 
            description=f"**{track_info['title']}** (คิวที่ {len(bot.queues_data[guild_id])})", 
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=embed)
    else:
        vc.play(discord.FFmpegPCMAudio(track_info['url'], **FFMPEG_OPTIONS), 
                after=lambda e: play_next(interaction, guild_id))
        embed = discord.Embed(
            title="🎵 กำลังเล่นเพลง", 
            description=f"**{track_info['title']}**", 
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed, view=MusicControlView())

bot.run(os.getenv("DISCORD_TOKEN"))
