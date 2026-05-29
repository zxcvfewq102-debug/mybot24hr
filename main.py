import discord
import os
from discord.ext import commands
import wavelink

# ตั้งค่า Intents
intents = discord.Intents.default()
intents.message_content = True

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 1. เชื่อมต่อ Lavalink (ต้องมีไฟล์ requirements.txt เพื่อให้รู้จัก wavelink)
        node = wavelink.Node(
            uri="https://lavalinkv4.serenetia.com",
            password="https://seretia.link/discord"
        )
        await wavelink.Pool.connect(client=self, nodes=[node])
        
        # 2. Sync คำสั่ง (ใส่ ID เซิร์ฟเวอร์ของคุณ)
        MY_GUILD_ID = discord.Object(id=1204647300870311986) 
        self.tree.copy_global_to(guild=MY_GUILD_ID)
        await self.tree.sync(guild=MY_GUILD_ID)
        
        print("Bot is ready and Commands Synced to your server!")

bot = MusicBot()

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
            await player.disconnect()
            await interaction.response.send_message("หยุดเพลงแล้ว", ephemeral=True)

@bot.tree.command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("ต้องอยู่ในห้องเสียงก่อนครับ!", ephemeral=True)
    
    await interaction.response.defer()
    
    player = wavelink.Pool.get_node().get_player(interaction.guild.id)
    if not player:
        player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
    
    tracks = await wavelink.Playable.search(query)
    if not tracks:
        return await interaction.followup.send("ไม่พบเพลงนี้ครับ")
    
    await player.play(tracks[0])
    
    embed = discord.Embed(title="🎵 กำลังเล่นเพลง", description=f"**{tracks[0].title}**", color=discord.Color.blue())
    await interaction.followup.send(embed=embed, view=MusicControlView())

# รันบอทโดยดึงค่าจาก Railway Variables
bot.run(os.getenv("DISCORD_TOKEN"))
