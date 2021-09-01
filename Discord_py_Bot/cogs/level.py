import discord
import os
import json
from discord import Member
from discord.ext import commands
from pymongo import MongoClient
from typing import Optional

level = ['Level-5+', 'Level-10+', 'Level-15+', 'Level-20+', 'Level-25+', 'Level-30+', 'Level-40+', 'Level-50+', 'Level-75+', 'Level-100+', 'Level-150+']
levelnum = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150]

my_secret = os.environ['clusterr']
cluster = MongoClient(my_secret)

levelling = cluster["DiscordBot"]["Levelling"]

class Levelsys(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print('Levelling System Now Online!')

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.guild is not None:
      if not message.content.startswith('?'):
        if not message.author.bot:
          stats = levelling.find_one({"id":message.author.id})
          if stats is None:
            newuser = {"id":message.author.id, "xp":100}
            levelling.insert_one(newuser)
          else:
            xp = stats["xp"] + 25
            levelling.update_one({"id":message.author.id}, {"$set":{"xp":xp}})
            lvl = 0
            while True:
              if xp < ((50*(lvl**2))+(50*lvl)):
                break
              lvl +=1
            xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
            if xp <= 0:
              await message.channel.send(f"{message.author.mention} Just Leveled Up To **Level: {lvl}**!")
              with open("jsons/mainBank.json", "r") as f:
                users = json.load(f)
              users[str(message.author.id)]["bank"] += int(lvl*1000)
              with open("jsons/mainBank.json", "w") as f:
                json.dump(users, f)
              for i in range(len(level)):
                if lvl == levelnum[i]:
                  await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))
                  mbed = discord.Embed(title=f"{message.author.mention} You Have Gotten role **{level[i]}**!", color = discord.Color.from_rgb(102, 204, 255))
                  mbed.set_thumbnail(url=message.author.avatar_url)
                  await message.channel.send(embed=mbed)
    else:
      return

  @commands.command()
  async def rank(self, ctx, target: Optional[Member]):
    user = target or ctx.author
    stats = levelling.find_one({"id":user.id})
    if stats is None:
      await ctx.channel.send(f"You Have't Sent Any Messages {user.mention}")
    else:
      xp = stats["xp"]
      lvl = 0
      rank = 0
      while True:
        if xp < ((50*(lvl**2))+(50*lvl)):
            break
        lvl +=1
      xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
      boxes = int((xp/(200*((1/2)*lvl)))*20)
      rankings = levelling.find().sort("xp",-1)
      for x in rankings:
        rank += 1
        if stats["id"] == x["id"]:
          break
      mbed = discord.Embed(title="{}'s level stats".format(user.name), color=discord.Color.from_rgb(102, 204, 255))
      mbed.add_field(name="Name", value=user.mention, inline=True)
      mbed.add_field(name="XP", value=f"{xp}/{int(200*((1/2)*lvl))}", inline=True)
      mbed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
      mbed.add_field(name="Level", value=f"{lvl}", inline=True)
      mbed.add_field(name="Progress Bar [lvl]", value=boxes*":blue_square:"+(20-boxes)*":white_large_square:" , inline=False)
      mbed.set_thumbnail(url=user.avatar_url)
      await ctx.send(embed = mbed)

  @commands.command()
  async def leaderboard(self, ctx):
    rankings = levelling.find().sort("xp",-1)
    i = 1
    mbed = discord.Embed(title="Rankings: ", color = discord.Color.from_rgb(102, 204, 255))
    for x in rankings:
      try:
        temp = ctx.guild.get_member(x["id"])
        tempxp = x["xp"]
        lvl = 0
        while True:
          if tempxp < ((50*(lvl**2))+(50*lvl)):
            break
          lvl +=1
        mbed.add_field(name=f"{i}: {temp.name}", value=f"Level: {lvl}")
      except:
        pass
      if i == 11:
        break
    await ctx.send(embed = mbed)
    


def setup(client):
  client.add_cog(Levelsys(client))

