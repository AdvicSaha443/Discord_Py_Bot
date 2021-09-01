import asyncio
import time
import typing as t
from datetime import datetime

import discord
import youtube_dl
import os
import aiohttp

from discord.ext import commands

LYRICS_URL = "https://some-random-api.ml/lyrics?title="

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        os.remove(filename)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      print('Music Bot Ready!')

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        mbed = discord.Embed(
          title = f"Joined {channel}",
          color = discord.Color.from_rgb(102, 204, 255)
        )

        await channel.connect()
        await ctx.send(embed = mbed)
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        #source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        #ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'This Command Is Under Testing! Use ?yt [Music Name]')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
          try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
          except:
            await ctx.send("Unable To Play This Song Plz Try Again.")
        
        mbed = discord.Embed(
          title= f"Now Playing: {player.title}",
          color = discord.Color.from_rgb(102, 204, 255),
        )

        await ctx.send(embed = mbed)
        await deletefile()

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        mbed = discord.Embed(
          title= f"Changed volume to {volume}%",
          color = discord.Color.from_rgb(102, 204, 255),
        )

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(embed = mbed)

    @commands.command()
    async def pause(self, ctx):     
      if ctx.voice_client.is_playing:
        ctx.voice_client.pause()
        await ctx.message.add_reaction('⏸️')
    
    @commands.command()
    async def resume(self, ctx):
      if ctx.voice_client.is_playing:
        ctx.voice_client.resume()
        await ctx.message.add_reaction('⏯')

    @commands.command()
    async def stop(self ,ctx):
      if ctx.voice_client.is_playing:
        ctx.voice_client.stop()
        await ctx.message.add_reaction('🛑')

    @commands.command(name="lyrics")
    async def lyrics_command(self, ctx, name: t.Optional[str]):
      name = name or ctx.voice_client.current_track.title

      async with ctx.typing():
        async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
          if not 200 < r.status < 299:
            ctx.send('No Lyrics Found')

          data = await r.json()

          if len(data['lyrics']) > 2000:
            return await ctx.send(f"<{data['links']['genius']}>")

          mbed = discord.Embed(
            title = data['title'],
            description = data['lyrics'],
            color=discord.Color.from_rgb(102, 204, 255),
            timestamp = datetime.utcnow(),
          )
          mbed.set_thumbnail(url=data["thumbnail"]["genius"])
          mbed.set_author(name=data["author"])
          await ctx.send(embed = mbed)




    @commands.command()
    async def disconnect(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected!")

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(client):
  client.add_cog(Music(client))


async def deletefile():
  for filename in os.listdir('./'):
    if filename.startswith('youtube-'):
      await asyncio.sleep(5)
      os.remove(filename)