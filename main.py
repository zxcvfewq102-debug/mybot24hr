import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import yt_dlp
import asyncio
from datetime import datetime, timezone
import random
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

queues = {}
now_playing = {}
control_messages = {}
start_times = {}

COLORS = {
    'primary': 0x7289DA,
    'success': 0x43B581,
    'warning': 0xFAA61A,
    'danger': 0xF04747,
    'info': 0x00D9FF,
    'purple': 0x9B59B6,
    'gold': 0xFFD700,
    'pink': 0xFF69B4,
    'cyan': 0x00FFFF,
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
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
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

def format_duration(seconds):
    if not seconds:
        return "ไม่ทราบ"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins:02d}:{secs:02d}"

def get_progress_bar(current, total, length=20):
    if total == 0 or current > total:
        return "━" * length
    filled = max(0, min(int(length * current / total), length))
    if filled == 0:
        return "○" + "─" * (length - 1)
    elif filled >= length:
        return "━" * length
    return "━" * filled + "○" + "─" * (length - filled - 1)

def create_simple_embed(title, description, color=COLORS['primary'], emoji="`✨`"):
    embed = discord.Embed(
        title=f"{emoji} {title}",
        description=f"> {description}",
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="🎵 Music Bot", icon_url="https://cdn-icons-png.flaticon.com/512/727/727245.png")
    return embed

def create_now_playing_embed(ctx):
    guild_id = ctx.guild.id
    if guild_id not in now_playing:
        return None

    player = now_playing[guild_id]
    duration = format_duration(player.duration)
    elapsed = 0
    
    if guild_id in start_times and ctx.voice_client and ctx.voice_client.is_playing():
        elapsed = int(time.time() - start_times[guild_id])
    
    elapsed_str = format_duration(elapsed)
    progress_bar = get_progress_bar(elapsed, player.duration if player.duration else 0)

    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            status = "กำลังเล่น"
            status_emoji = "`▶️`"
            status_color = COLORS['gold']
        elif ctx.voice_client.is_paused():
            status = "หยุดชั่วคราว"
            status_emoji = "`⏸️`"
            status_color = COLORS['warning']
        else:
            status = "หยุด"
            status_emoji = "`⏹️`"
            status_color = COLORS['danger']
    else:
        status = "ไม่ได้เชื่อมต่อ"
        status_emoji = "`❌`"
        status_color = COLORS['danger']

    embed = discord.Embed(
        title=f"{status_emoji} {status}",
        color=status_color,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="`🎵` กำลังเล่น",
        value=f"**[{player.title}]({player.webpage_url})**",
        inline=False
    )

    embed.add_field(
        name="`⏱️` ความคืบหน้า",
        value=f"`{elapsed_str}` {progress_bar} `{duration}`",
        inline=False
    )

    current_volume = 50
    if ctx.voice_client and ctx.voice_client.source and hasattr(ctx.voice_client.source, 'volume'):
        current_volume = int(ctx.voice_client.source.volume * 100)

    volume_emoji = "🔇" if current_volume == 0 else "🔉" if current_volume < 50 else "🔊"

    info_text = f"{volume_emoji} **ระดับเสียง:** `{current_volume}%`\n"
    info_text += f"`📊` **คิว:** `{len(queues[guild_id]) if guild_id in queues else 0} เพลง`"
    embed.add_field(name="`⚙️` สถานะ", value=info_text, inline=True)

    song_info = f"`👤` **ช่อง:** {player.uploader}\n"
    if player.requester:
        song_info += f"`🎤` **ขอโดย:** {player.requester.mention}"
    embed.add_field(name="`📝` รายละเอียด", value=song_info, inline=True)

    if player.thumbnail:
        embed.set_image(url=player.thumbnail)

    embed.set_footer(
        text="ใช้ปุ่มด้านล่างเพื่อควบคุม",
        icon_url="https://cdn-icons-png.flaticon.com/512/727/727245.png"
    )

    return embed

class MusicControlView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    async def update_now_playing(self):
        guild_id = self.ctx.guild.id
        if guild_id in control_messages and guild_id in now_playing:
            try:
                embed = create_now_playing_embed(self.ctx)
                await control_messages[guild_id].edit(embed=embed)
            except:
                pass

    @discord.ui.button(emoji="⏸️", label="หยุด", style=discord.ButtonStyle.primary, custom_id="pause")
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            await self.update_now_playing()
            embed = create_simple_embed("หยุดชั่วคราว", "หยุดเพลงชั่วคราวแล้ว", COLORS['warning'], "`⏸️`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_simple_embed("ไม่สามารถหยุดได้", "ไม่มีเพลงที่กำลังเล่นอยู่", COLORS['danger'], "`❌`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="▶️", label="เล่นต่อ", style=discord.ButtonStyle.success, custom_id="resume")
    async def resume_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            await self.update_now_playing()
            embed = create_simple_embed("เล่นต่อ", "เล่นเพลงต่อแล้ว", COLORS['success'], "`▶️`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_simple_embed("ไม่สามารถเล่นต่อได้", "เพลงไม่ได้หยุดอยู่", COLORS['danger'], "`❌`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="⏭️", label="ข้าม", style=discord.ButtonStyle.secondary, custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            embed = create_simple_embed("ข้ามเพลง", "ข้ามไปเพลงถัดไปแล้ว", COLORS['info'], "`⏭️`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_simple_embed("ไม่สามารถข้ามได้", "ไม่มีเพลงที่กำลังเล่นอยู่", COLORS['danger'], "`❌`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="⏹️", label="หยุดทั้งหมด", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        guild_id = self.ctx.guild.id
        queue_count = len(queues[guild_id]) if guild_id in queues else 0

        if guild_id in queues:
            queues[guild_id].clear()

        if self.ctx.voice_client:
            self.ctx.voice_client.stop()

        embed = create_simple_embed(
            "หยุดการเล่น",
            f"หยุดเพลงและล้างคิว ({queue_count} เพลง) แล้ว",
            COLORS['danger'],
            "`⏹️`"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="📝", label="คิว", style=discord.ButtonStyle.secondary, custom_id="queue")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        guild_id = self.ctx.guild.id

        if guild_id not in queues or len(queues[guild_id]) == 0:
            embed = create_simple_embed("คิวว่าง", "ไม่มีเพลงในคิว", COLORS['info'], "`📭`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        queue_list = ""
        for i, song in enumerate(queues[guild_id][:10], 1):
            queue_list += f"`{i}.` **{song.title}**\n"

        if len(queues[guild_id]) > 10:
            queue_list += f"\n`✨` *...และอีก {len(queues[guild_id]) - 10} เพลง*"

        embed = discord.Embed(
            title="`📝` รายการคิว",
            description=queue_list,
            color=COLORS['purple'],
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="`📊` สถิติ",
            value=f"`🎵` **จำนวนเพลง:** `{len(queues[guild_id])}` เพลง",
            inline=False
        )

        embed.set_footer(text=f"ดูโดย {interaction.user.display_name}",
                        icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed, ephemeral=True)

class VolumeControlView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    async def update_volume_display(self, interaction, vol):
        if not self.ctx.voice_client:
            embed = create_simple_embed("ไม่ได้เชื่อมต่อ", "บอทไม่ได้อยู่ในห้องเสียง", COLORS['danger'], "`❌`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self.ctx.voice_client.source or not hasattr(self.ctx.voice_client.source, 'volume'):
            embed = create_simple_embed("ไม่สามารถปรับได้", "ไม่มีเพลงที่กำลังเล่นอยู่", COLORS['danger'], "`❌`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.ctx.voice_client.source.volume = vol / 100

        emoji = "🔇" if vol == 0 else "🔉" if vol < 50 else "🔊"
        bar_length = 20
        filled = int(bar_length * vol / 100)
        volume_bar = "█" * filled + "░" * (bar_length - filled)

        embed = discord.Embed(
            title=f"{emoji} ควบคุมระดับเสียง",
            description=f"> กำลังปรับระดับเสียงของบอท",
            color=COLORS['info'],
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="`🎚️` ระดับเสียงปัจจุบัน",
            value=f"{vol}%\n`{volume_bar}`",
            inline=False
        )

        embed.add_field(
            name="`💡` เคล็ดลับ",
            value="ใช้ปุ่มด้านล่างเพื่อเปลี่ยนระดับเสียงอย่างรวดเร็ว!",
            inline=False
        )

        embed.set_footer(
            text=f"ปรับโดย {interaction.user.display_name}",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )

        await interaction.response.edit_message(embed=embed)

        guild_id = self.ctx.guild.id
        if guild_id in control_messages:
            try:
                np_embed = create_now_playing_embed(self.ctx)
                await control_messages[guild_id].edit(embed=np_embed)
            except:
                pass

    @discord.ui.button(emoji="🔇", label="0%", style=discord.ButtonStyle.secondary)
    async def vol_0(self, interaction: discord.Interaction, button: Button):
        await self.update_volume_display(interaction, 0)

    @discord.ui.button(emoji="🔉", label="25%", style=discord.ButtonStyle.primary)
    async def vol_25(self, interaction: discord.Interaction, button: Button):
        await self.update_volume_display(interaction, 25)

    @discord.ui.button(emoji="🔉", label="50%", style=discord.ButtonStyle.primary)
    async def vol_50(self, interaction: discord.Interaction, button: Button):
        await self.update_volume_display(interaction, 50)

    @discord.ui.button(emoji="🔊", label="75%", style=discord.ButtonStyle.success)
    async def vol_75(self, interaction: discord.Interaction, button: Button):
        await self.update_volume_display(interaction, 75)

    @discord.ui.button(emoji="🔊", label="100%", style=discord.ButtonStyle.danger)
    async def vol_100(self, interaction: discord.Interaction, button: Button):
        await self.update_volume_display(interaction, 100)

@tasks.loop(seconds=0)
async def update_now_playing_task():
    for guild_id, message in list(control_messages.items()):
        if guild_id in now_playing:
            try:
                guild = bot.get_guild(guild_id)
                if guild and guild.voice_client:
                    class MockCtx:
                        def __init__(self, guild):
                            self.guild = guild
                            self.voice_client = guild.voice_client

                    ctx = MockCtx(guild)
                    embed = create_now_playing_embed(ctx)
                    if embed:
                        await message.edit(embed=embed)
            except:
                pass

@bot.event
async def on_ready():
    print(f'🎵 {bot.user} พร้อมเล่นเพลงแล้ว!')
    print(f'📊 เชื่อมต่อกับ {len(bot.guilds)} เซิร์ฟเวอร์')
    
    if not update_now_playing_task.is_running():
        update_now_playing_task.start()
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="!help ดูคำสั่งบอทเพลง"
        )
    )

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    if not ctx.author.voice:
        embed = create_simple_embed(
            "ไม่สามารถเล่นได้",
            "คุณต้องเข้าร่วมห้องเสียงก่อนใช้คำสั่งนี้!",
            COLORS['danger'],
            "`❌`"
        )
        return await ctx.send(embed=embed)

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    loading_embed = discord.Embed(
        title="`⏳` กำลังค้นหา",
        description=f"> กำลังค้นหา **{query}**...\n> กรุณารอสักครู่",
        color=COLORS['info'],
        timestamp=datetime.now(timezone.utc)
    )
    loading_embed.set_footer(text="🔍 กำลังประมวลผล...")
    loading = await ctx.send(embed=loading_embed)

    try:
        if not query.startswith('http'):
            query = f"ytsearch:{query}"

        player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
        player.requester = ctx.author

        guild_id = ctx.guild.id
        if guild_id not in queues:
            queues[guild_id] = []

        queues[guild_id].append(player)

        if not ctx.voice_client.is_playing():
            try:
                await loading.delete()
            except:
                pass
            await play_next(ctx)
        else:
            success_embed = discord.Embed(
                title="`✅` เพิ่มเข้าคิวแล้ว",
                description=f"> **[{player.title}]({player.webpage_url})**",
                color=COLORS['success'],
                timestamp=datetime.now(timezone.utc)
            )

            success_embed.add_field(
                name="`📊` ข้อมูล",
                value=f"`👤` **ช่อง:** {player.uploader}\n`⏱️` **ระยะเวลา:** {format_duration(player.duration)}\n`📝` **ตำแหน่งในคิว:** #{len(queues[guild_id])}",
                inline=False
            )

            success_embed.add_field(
                name="`🎤` ขอโดย",
                value=ctx.author.mention,
                inline=True
            )

            if player.thumbnail:
                success_embed.set_thumbnail(url=player.thumbnail)

            success_embed.set_footer(
                text=f"ขอโดย {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )

            await loading.edit(embed=success_embed)

            if guild_id in control_messages:
                try:
                    embed = create_now_playing_embed(ctx)
                    await control_messages[guild_id].edit(embed=embed)
                except:
                    pass

    except Exception as e:
        error_embed = discord.Embed(
            title="`❌` เกิดข้อผิดพลาด",
            description=f"> ไม่สามารถเล่นเพลงได้",
            color=COLORS['danger'],
            timestamp=datetime.now(timezone.utc)
        )

        error_embed.add_field(
            name="`📝` รายละเอียด",
            value=f"```{str(e)[:200]}```",
            inline=False
        )

        error_embed.set_footer(text="💡 ลองใช้คำค้นหาอื่นหรือลิงก์ที่ถูกต้อง")
        await loading.edit(embed=error_embed)

async def play_next(ctx):
    guild_id = ctx.guild.id
    
    if guild_id in queues and len(queues[guild_id]) > 0:
        player = queues[guild_id].pop(0)
        now_playing[guild_id] = player
        start_times[guild_id] = time.time()

        def after_playing(error):
            if error:
                print(f'Error: {error}')
            coro = play_next(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except:
                pass

        ctx.voice_client.play(player, after=after_playing)

        embed = create_now_playing_embed(ctx)
        view = MusicControlView(ctx)

        if guild_id in control_messages:
            try:
                await control_messages[guild_id].delete()
            except:
                pass

        message = await ctx.send(embed=embed, view=view)
        control_messages[guild_id] = message
    else:
        if ctx.voice_client:
            now_playing.pop(guild_id, None)
            start_times.pop(guild_id, None)
            
            if guild_id in control_messages:
                try:
                    await control_messages[guild_id].delete()
                except:
                    pass
                control_messages.pop(guild_id, None)
            
            embed = discord.Embed(
                title="`👋` เพลงหมดแล้ว",
                description="> ไม่มีเพลงในคิวแล้ว บอทจะออกจากห้องเสียง",
                color=COLORS['info'],
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="🎵 ใช้ !play เพื่อเล่นเพลงอีกครั้ง")
            await ctx.send(embed=embed)
            
            await asyncio.sleep(2)
            await ctx.voice_client.disconnect()

@bot.command(name='volume', aliases=['vol', 'v'])
async def volume(ctx, vol: int = None):
    if vol is None:
        current_vol = 50
        if ctx.voice_client and ctx.voice_client.source:
            current_vol = int(ctx.voice_client.source.volume * 100)

        emoji = "🔇" if current_vol == 0 else "🔉" if current_vol < 50 else "🔊"
        bar_length = 20
        filled = int(bar_length * current_vol / 100)
        volume_bar = "█" * filled + "░" * (bar_length - filled)

        embed = discord.Embed(
            title=f"{emoji} ควบคุมระดับเสียง",
            description="> ใช้ปุ่มด้านล่างเพื่อปรับระดับเสียง\n> **การเปลี่ยนแปลงจะมีผลทันที!**",
            color=COLORS['info'],
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="`🎚️` ระดับเสียงปัจจุบัน",
            value=f"{current_vol}%\n`{volume_bar}`",
            inline=False
        )

        embed.set_footer(text="🎵 Music Bot • Real-time Control")
        view = VolumeControlView(ctx)
        return await ctx.send(embed=embed, view=view)

    if not ctx.voice_client:
        embed = create_simple_embed(
            "ไม่สามารถปรับได้",
            "บอทไม่ได้อยู่ในห้องเสียง",
            COLORS['danger'],
            "`❌`"
        )
        return await ctx.send(embed=embed)

    if 0 <= vol <= 100:
        if ctx.voice_client.source and hasattr(ctx.voice_client.source, 'volume'):
            ctx.voice_client.source.volume = vol / 100

            emoji = "🔇" if vol == 0 else "🔉" if vol < 50 else "🔊"
            bar_length = 20
            filled = int(bar_length * vol / 100)
            volume_bar = "█" * filled + "░" * (bar_length - filled)

            embed = discord.Embed(
                title=f"{emoji} ปรับระดับเสียงแล้ว",
                description=f"> ตั้งระดับเสียงเป็น **{vol}%**",
                color=COLORS['success'],
                timestamp=datetime.now(timezone.utc)
            )

            embed.add_field(
                name="`🎚️` ระดับเสียงใหม่",
                value=f"`{volume_bar}` **{vol}%**",
                inline=False
            )

            embed.set_footer(
                text=f"ปรับโดย {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )

            await ctx.send(embed=embed)
        else:
            embed = create_simple_embed(
                "ไม่สามารถปรับได้",
                "ไม่มีเพลงที่กำลังเล่นอยู่",
                COLORS['danger'],
                "`❌`"
            )
            await ctx.send(embed=embed)

        guild_id = ctx.guild.id
        if guild_id in control_messages:
            try:
                np_embed = create_now_playing_embed(ctx)
                await control_messages[guild_id].edit(embed=np_embed)
            except:
                pass
    else:
        embed = create_simple_embed(
            "ค่าไม่ถูกต้อง",
            "ระดับเสียงต้องอยู่ระหว่าง **0-100**",
            COLORS['danger'],
            "`❌`"
        )
        await ctx.send(embed=embed)

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        embed = create_simple_embed("หยุดชั่วคราว", "หยุดเพลงชั่วคราวแล้ว", COLORS['warning'], "`⏸️`")
        await ctx.send(embed=embed)

        guild_id = ctx.guild.id
        if guild_id in control_messages:
            try:
                np_embed = create_now_playing_embed(ctx)
                await control_messages[guild_id].edit(embed=np_embed)
            except:
                pass
    else:
        embed = create_simple_embed("ไม่สามารถหยุดได้", "ไม่มีเพลงที่กำลังเล่นอยู่", COLORS['danger'], "`❌`")
        await ctx.send(embed=embed)

@bot.command(name='resume', aliases=['r'])
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        embed = create_simple_embed("เล่นต่อ", "เล่นเพลงต่อแล้ว", COLORS['success'], "`▶️`")
        await ctx.send(embed=embed)

        guild_id = ctx.guild.id
        if guild_id in control_messages:
            try:
                np_embed = create_now_playing_embed(ctx)
                await control_messages[guild_id].edit(embed=np_embed)
            except:
                pass
    else:
        embed = create_simple_embed("ไม่สามารถเล่นต่อได้", "เพลงไม่ได้หยุดอยู่", COLORS['danger'], "`❌`")
        await ctx.send(embed=embed)

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        guild_id = ctx.guild.id
        next_count = len(queues[guild_id]) if guild_id in queues else 0

        ctx.voice_client.stop()

        embed = discord.Embed(
            title="`⏭️` ข้ามเพลง",
            description="> ข้ามไปเพลงถัดไปแล้ว",
            color=COLORS['info'],
            timestamp=datetime.now(timezone.utc)
        )

        if next_count > 0:
            embed.add_field(
                name="`📝` เพลงถัดไป",
                value=f"`{next_count}` เพลงในคิว",
                inline=False
            )

        embed.set_footer(
            text=f"ขอโดย {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        await ctx.send(embed=embed)
    else:
        embed = create_simple_embed("ไม่สามารถข้ามได้", "ไม่มีเพลงที่กำลังเล่นอยู่", COLORS['danger'], "`❌`")
        await ctx.send(embed=embed)

@bot.command(name='stop')
async def stop(ctx):
    guild_id = ctx.guild.id
    queue_count = len(queues[guild_id]) if guild_id in queues else 0

    if guild_id in queues:
        queues[guild_id].clear()

    if ctx.voice_client:
        ctx.voice_client.stop()

    embed = discord.Embed(
        title="`⏹️` หยุดการเล่น",
        description="> หยุดเพลงและล้างคิวทั้งหมดแล้ว",
        color=COLORS['danger'],
        timestamp=datetime.now(timezone.utc)
    )

    if queue_count > 0:
        embed.add_field(
            name="`📝` ล้างคิว",
            value=f"ลบ `{queue_count}` เพลงออกจากคิว",
            inline=False
        )

    embed.set_footer(
        text=f"ขอโดย {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

@bot.command(name='join', aliases=['j'])
async def join(ctx):
    if not ctx.author.voice:
        embed = create_simple_embed(
            "ไม่สามารถเข้าร่วมได้",
            "คุณต้องอยู่ในห้องเสียงก่อน!",
            COLORS['danger'],
            "`❌`"
        )
        return await ctx.send(embed=embed)

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    embed = discord.Embed(
        title="`✅` เชื่อมต่อแล้ว",
        description=f"> เข้าร่วมห้องเสียง **{channel.name}** แล้ว",
        color=COLORS['success'],
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="`🎵` พร้อมเล่นเพลง",
        value=f"ใช้ `!play` เพื่อเริ่มเล่นเพลง",
        inline=False
    )

    embed.set_footer(
        text=f"เชิญโดย {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

@bot.command(name='leave', aliases=['dc'])
async def leave(ctx):
    if ctx.voice_client:
        guild_id = ctx.guild.id
        queue_count = len(queues[guild_id]) if guild_id in queues else 0

        for key in [queues, now_playing, control_messages, start_times]:
            key.pop(guild_id, None)

        channel_name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()

        embed = discord.Embed(
            title="`👋` ออกจากห้องเสียง",
            description=f"> ออกจากห้องเสียง **{channel_name}** แล้ว",
            color=COLORS['info'],
            timestamp=datetime.now(timezone.utc)
        )

        if queue_count > 0:
            embed.add_field(
                name="`📝` ล้างข้อมูล",
                value=f"ลบคิว `{queue_count}` เพลงและข้อมูลทั้งหมด",
                inline=False
            )

        embed.set_footer(
            text=f"ขอโดย {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        await ctx.send(embed=embed)
    else:
        embed = create_simple_embed(
            "ไม่สามารถออกได้",
            "บอทไม่ได้อยู่ในห้องเสียง",
            COLORS['danger'],
            "`❌`"
        )
        await ctx.send(embed=embed)

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    guild_id = ctx.guild.id

    if guild_id not in queues or not queues[guild_id]:
        embed = create_simple_embed("คิวว่าง", "ไม่มีเพลงในคิว ใช้ `!play` เพื่อเพิ่มเพลง", COLORS['info'], "`📭`")
        return await ctx.send(embed=embed)

    queue_list = ""
    total_duration = 0

    for i, song in enumerate(queues[guild_id][:10], 1):
        duration = format_duration(song.duration)
        queue_list += f"`{i}.` **{song.title}** `[{duration}]`\n"
        total_duration += song.duration if song.duration else 0

    if len(queues[guild_id]) > 10:
        remaining = len(queues[guild_id]) - 10
        queue_list += f"\n`✨` *...และอีก {remaining} เพลง*"

    embed = discord.Embed(
        title="`📝` รายการคิว",
        description=queue_list,
        color=COLORS['purple'],
        timestamp=datetime.now(timezone.utc)
    )

    stats = f"`🎵` **จำนวน:** `{len(queues[guild_id])}` เพลง\n"
    stats += f"`⏱️` **เวลารวม:** `{format_duration(total_duration)}`"
    embed.add_field(name="`📊` สถิติ", value=stats, inline=False)

    embed.set_footer(
        text=f"ดูโดย {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

@bot.command(name='nowplaying', aliases=['np'])
async def nowplaying(ctx):
    guild_id = ctx.guild.id

    if guild_id in now_playing and ctx.voice_client and ctx.voice_client.is_playing():
        embed = create_now_playing_embed(ctx)
        view = MusicControlView(ctx)
        await ctx.send(embed=embed, view=view)
    else:
        embed = create_simple_embed(
            "ไม่มีเพลง",
            "ไม่มีเพลงที่กำลังเล่นอยู่ ใช้ `!play` เพื่อเล่นเพลง",
            COLORS['danger'],
            "`❌`"
        )
        await ctx.send(embed=embed)

@bot.command(name='help', aliases=['h'])
async def help_cmd(ctx):
    embed = discord.Embed(
        title="`🎵` คำสั่งบอทเพลง",
        description="> **บอทเพลงที่อัพเดทแบบเรียลไทม์!**\n> ใช้ปุ่มและคำสั่งด้านล่างเพื่อควบคุมเพลง",
        color=COLORS['primary'],
        timestamp=datetime.now(timezone.utc)
    )

    basic_commands = (
        "`!play <เพลง/URL>` - เล่นเพลง\n"
        "`!pause` - หยุดชั่วคราว\n"
        "`!resume` - เล่นต่อ\n"
        "`!skip` - ข้ามเพลง\n"
        "`!stop` - หยุดและล้างคิว"
    )
    embed.add_field(name="`🎮` คำสั่งพื้นฐาน", value=basic_commands, inline=False)

    queue_commands = (
        "`!queue` - แสดงคิว\n"
        "`!nowplaying` - เพลงปัจจุบัน"
    )
    embed.add_field(name="`📝` คิวและข้อมูล", value=queue_commands, inline=True)

    connection_commands = (
        "`!join` - เข้าห้องเสียง\n"
        "`!leave` - ออกห้องเสียง"
    )
    embed.add_field(name="`🔌` การเชื่อมต่อ", value=connection_commands, inline=True)

    settings_commands = (
        "`!volume [0-100]` - ปรับเสียง"
    )
    embed.add_field(name="`⚙️` ตั้งค่า", value=settings_commands, inline=False)

    features = (
        "`🎚️` ปรับเสียง\n"
        "`🎮` ปุ่มควบคุมแบบ Interactive\n"
        "`🚪` ออกอัตโนมัติเมื่อเพลงหมด"
    )
    embed.add_field(name="`✨` ฟีเจอร์พิเศษ", value=features, inline=False)

    aliases_text = "`!p` = play, `!s` = skip, `!r` = resume, `!q` = queue, `!np` = nowplaying, `!v` = volume"
    embed.add_field(name="`💡` คำสั่งลัด", value=aliases_text, inline=False)

    embed.set_footer(
        text="🎵 Music Bot",
        icon_url="https://cdn-icons-png.flaticon.com/512/727/727245.png"
    )

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    await ctx.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and before.channel and not after.channel:
        guild_id = before.channel.guild.id
        for key in [queues, now_playing, control_messages, start_times]:
            key.pop(guild_id, None)

if __name__ == "__main__":
    TOKEN = '' 
    
load_dotenv()
bot.run(os.getenv('TOKEN'))
