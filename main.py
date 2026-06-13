import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
import yt_dlp
import asyncio
from datetime import datetime, timezone
import random
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

queues = {}
now_playing = {}
control_messages = {}
start_times = {}

COLORS = {
    'primary': 0x7289DA, 'success': 0x43B581, 'warning': 0xFAA61A,
    'danger': 0xF04747, 'info': 0x00D9FF, 'purple': 0x9B59B6,
    'gold': 0xFFD700, 'pink': 0xFF69B4, 'cyan': 0x00FFFF,
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 'restrictfilenames': True,
    'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False,
    'logtostderr': False, 'quiet': True, 'no_warnings': True,
    'default_search': 'auto', 'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration', 0)
        self.uploader = data.get('uploader', 'Unknown')
        self.webpage_url = data.get('webpage_url')
        self.requester = None

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

def format_duration(seconds):
    if not seconds: return "ไม่ทราบ"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins:02d}:{secs:02d}"

def get_progress_bar(current, total, length=20):
    if total == 0 or current > total: return "━" * length
    filled = max(0, min(int(length * current / total), length))
    return ("━" * filled + "○" + "─" * (length - filled - 1)) if filled < length else "━" * length

def create_simple_embed(title, description, color=COLORS['primary'], emoji="`✨`"):
    embed = discord.Embed(title=f"{emoji} {title}", description=f"> {description}", color=color, timestamp=datetime.now(timezone.utc))
    embed.set_footer(text="🎵 Music Bot")
    return embed

def create_now_playing_embed(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id not in now_playing: return None
    player = now_playing[guild_id]
    duration = format_duration(player.duration)
    elapsed = int(time.time() - start_times.get(guild_id, time.time())) if guild_id in start_times else 0
    progress_bar = get_progress_bar(elapsed, player.duration or 0)
    
    embed = discord.Embed(title="`▶️` กำลังเล่น", color=COLORS['gold'], timestamp=datetime.now(timezone.utc))
    embed.add_field(name="`🎵` เพลง", value=f"**[{player.title}]({player.webpage_url})**", inline=False)
    embed.add_field(name="`⏱️` ความคืบหน้า", value=f"`{format_duration(elapsed)}` {progress_bar} `{duration}`", inline=False)
    if player.thumbnail: embed.set_image(url=player.thumbnail)
    return embed

class MusicControlView(View):
    def __init__(self, interaction):
        super().__init__(timeout=None)
        self.interaction = interaction

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary, custom_id="pause")
    async def pause(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.pause()
        await interaction.response.send_message("หยุดชั่วคราวแล้ว", ephemeral=True)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success, custom_id="resume")
    async def resume(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.resume()
        await interaction.response.send_message("เล่นต่อแล้ว", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="skip")
    async def skip(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.stop()
        await interaction.response.send_message("ข้ามเพลงแล้ว", ephemeral=True)

@bot.tree.command(name='play', description='เล่นเพลงจากชื่อหรือลิงก์')
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    try:
        if not query.startswith('http'): query = f"ytsearch:{query}"
        player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
        player.requester = interaction.user
        guild_id = interaction.guild.id
        if guild_id not in queues: queues[guild_id] = []
        queues[guild_id].append(player)
        
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await play_next(interaction)
        await interaction.followup.send(f"เพิ่มเพลงลงคิว: {player.title}")
    except Exception as e:
        await interaction.followup.send(f"เกิดข้อผิดพลาด: ```{e}```")

async def play_next(interaction):
    guild_id = interaction.guild.id
    if guild_id in queues and queues[guild_id]:
        player = queues[guild_id].pop(0)
        now_playing[guild_id] = player
        start_times[guild_id] = time.time()
        vc = interaction.guild.voice_client
        if not vc: vc = await interaction.user.voice.channel.connect()
        vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop))
        embed = create_now_playing_embed(interaction)
        control_messages[guild_id] = await interaction.channel.send(embed=embed, view=MusicControlView(interaction))
    else:
        now_playing.pop(guild_id, None)

if __name__ == "__main__":
    bot.run('YOUR_BOT_TOKEN_HERE')import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
import yt_dlp
import asyncio
from datetime import datetime, timezone
import random
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

queues = {}
now_playing = {}
control_messages = {}
start_times = {}

COLORS = {
    'primary': 0x7289DA, 'success': 0x43B581, 'warning': 0xFAA61A,
    'danger': 0xF04747, 'info': 0x00D9FF, 'purple': 0x9B59B6,
    'gold': 0xFFD700, 'pink': 0xFF69B4, 'cyan': 0x00FFFF,
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 'restrictfilenames': True,
    'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False,
    'logtostderr': False, 'quiet': True, 'no_warnings': True,
    'default_search': 'auto', 'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration', 0)
        self.uploader = data.get('uploader', 'Unknown')
        self.webpage_url = data.get('webpage_url')
        self.requester = None

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

def format_duration(seconds):
    if not seconds: return "ไม่ทราบ"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins:02d}:{secs:02d}"

def get_progress_bar(current, total, length=20):
    if total == 0 or current > total: return "━" * length
    filled = max(0, min(int(length * current / total), length))
    return ("━" * filled + "○" + "─" * (length - filled - 1)) if filled < length else "━" * length

def create_simple_embed(title, description, color=COLORS['primary'], emoji="`✨`"):
    embed = discord.Embed(title=f"{emoji} {title}", description=f"> {description}", color=color, timestamp=datetime.now(timezone.utc))
    embed.set_footer(text="🎵 Music Bot")
    return embed

def create_now_playing_embed(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id not in now_playing: return None
    player = now_playing[guild_id]
    duration = format_duration(player.duration)
    elapsed = int(time.time() - start_times.get(guild_id, time.time())) if guild_id in start_times else 0
    progress_bar = get_progress_bar(elapsed, player.duration or 0)
    
    embed = discord.Embed(title="`▶️` กำลังเล่น", color=COLORS['gold'], timestamp=datetime.now(timezone.utc))
    embed.add_field(name="`🎵` เพลง", value=f"**[{player.title}]({player.webpage_url})**", inline=False)
    embed.add_field(name="`⏱️` ความคืบหน้า", value=f"`{format_duration(elapsed)}` {progress_bar} `{duration}`", inline=False)
    if player.thumbnail: embed.set_image(url=player.thumbnail)
    return embed

class MusicControlView(View):
    def __init__(self, interaction):
        super().__init__(timeout=None)
        self.interaction = interaction

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary, custom_id="pause")
    async def pause(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.pause()
        await interaction.response.send_message("หยุดชั่วคราวแล้ว", ephemeral=True)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success, custom_id="resume")
    async def resume(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.resume()
        await interaction.response.send_message("เล่นต่อแล้ว", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="skip")
    async def skip(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.stop()
        await interaction.response.send_message("ข้ามเพลงแล้ว", ephemeral=True)

@bot.tree.command(name='play', description='เล่นเพลงจากชื่อหรือลิงก์')
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    try:
        if not query.startswith('http'): query = f"ytsearch:{query}"
        player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
        player.requester = interaction.user
        guild_id = interaction.guild.id
        if guild_id not in queues: queues[guild_id] = []
        queues[guild_id].append(player)
        
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await play_next(interaction)
        await interaction.followup.send(f"เพิ่มเพลงลงคิว: {player.title}")
    except Exception as e:
        await interaction.followup.send(f"เกิดข้อผิดพลาด: ```{e}```")

async def play_next(interaction):
    guild_id = interaction.guild.id
    if guild_id in queues and queues[guild_id]:
        player = queues[guild_id].pop(0)
        now_playing[guild_id] = player
        start_times[guild_id] = time.time()
        vc = interaction.guild.voice_client
        if not vc: vc = await interaction.user.voice.channel.connect()
        vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop))
        embed = create_now_playing_embed(interaction)
        control_messages[guild_id] = await interaction.channel.send(embed=embed, view=MusicControlView(interaction))
    else:
        now_playing.pop(guild_id, None)

if __name__ == "__main__":
    bot.run('YOUR_BOT_TOKEN_HERE')
