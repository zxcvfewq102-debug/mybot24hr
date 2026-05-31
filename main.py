import discord
import os
from discord.ext import commands
import wavelink
import logging
import asyncio

# บังคับเปิด Logging เพื่อตรวจสอบการทำงาน
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # สร้างฟังก์ชันย่อยสำหรับเชื่อมต่อเป็น Background Task เพื่อไม่ให้ Railway สั่งปิดบอท
        async def connect_lavalink():
            node = wavelink.Node(
                uri="https://node.raidenbot.xyz:443", 
                password="https://dsc.gg/raidenbot"
            )
            try:
                logger.info("กำลังพยายามเชื่อมต่อกับ Lavalink Node (Background)...")
                await wavelink.Pool.connect(client=self, nodes=[node])
                logger.info("เชื่อมต่อ Lavalink สำเร็จแล้ว!")
            except Exception as e:
                logger.error(f"ไม่สามารถเชื่อมต่อ Lavalink ได้เนื่องจาก: {e}")

        # สั่งให้ทำงานเบื้องหลังทันที บอทหลักจะได้รันต่อได้ไม่โดนยื้อเวลา
        self.loop.create_task(connect_lavalink())
        
        # Sync คำสั่งไปยังเซิร์ฟเวอร์ของคุณ
        MY_GUILD_ID = discord.Object(id=1204647300870311986) 
        self.tree.copy_global_to(guild=MY_GUILD_ID)
        await self.tree.sync(guild=MY_GUILD_ID)
        
        print("Bot is ready and Commands Synced to your server!")

bot = MusicBot()

@bot.listen()
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    player = payload.player
    if not player:
        return

    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)
        
        if hasattr(player, "home_channel") and player.home_channel:
            embed = discord.Embed(
                title="🎵 กำลังเล่นเพลงถัดไป", 
                description=f"**{next_track.title}**", 
                color=discord.Color.green()
            )
            await player.home_channel.send(embed=embed, view=MusicControlView())

class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⏸️/▶️", style=discord.ButtonStyle.blurple)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = wavelink.Pool.get_node().get_player(interaction.guild.id)
        if player:
            await player.pause(not player.paused)
            await interaction.response.send_message("สลับโหมดเล่น/หยุด", ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = wavelink.Pool.get_node().get_player(interaction.guild.id)
        if player:
            player.queue.clear()
            await player.disconnect()
            await interaction.response.send_message("หยุดเพลงและล้างคิวแล้ว", ephemeral=True)

@bot.tree.command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("ต้องอยู่ในห้องเสียงก่อนครับ!", ephemeral=True)
    
    await interaction.response.defer()
    
    try:
        player = wavelink.Pool.get_node().get_player(interaction.guild.id)
        if not player:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            player.home_channel = interaction.channel 
        
        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await interaction.followup.send("ไม่พบเพลงนี้ครับ")
        
        track = tracks[0]

        if player.playing:
            player.queue.put(track)
            embed = discord.Embed(
                title="⏳ เพิ่มเข้าคิวแล้ว", 
                description=f"**{track.title}** (คิวที่ {player.queue.count})", 
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)
        else:
            await player.play(track)
            embed = discord.Embed(
                title="🎵 กำลังเล่นเพลง", 
                description=f"**{track.title}**", 
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed, view=MusicControlView())
            
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในคำสั่ง play: {e}")
        await interaction.followup.send("เกิดข้อผิดพลาดในระบบเล่นเพลง กรุณาลองใหม่อีกครั้ง")

bot.run(os.getenv("DISCORD_TOKEN"))
