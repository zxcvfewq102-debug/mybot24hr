@bot.slash_command(name="play", description="ค้นหาและเพิ่มเพลงเข้าคิว")
async def play(interaction: nextcord.Interaction, search: str):
    if not interaction.user.voice: 
        return await interaction.response.send_message("❌ ต้องเข้าห้องเสียงก่อนครับ")
    
    await interaction.response.defer()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ค้นหาเพลง
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            
            # ตรวจสอบว่า info มีข้อมูลหรือไม่
            entries = info.get('entries', [])
            if not entries:
                return await interaction.followup.send("❌ ไม่พบเพลงที่ค้นหาครับ ลองเปลี่ยนชื่อเพลงดูนะครับ")
            
            video = entries[0]
            
            # เชื่อมต่อห้องเสียง
            if not interaction.guild.voice_client: 
                await interaction.user.voice.channel.connect()
            
            url = video.get('url')
            source = await nextcord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            interaction.guild.voice_client.play(source)
            await interaction.followup.send(f"🎵 กำลังเล่น: {video.get('title')}")
            
    except Exception as e: 
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")
