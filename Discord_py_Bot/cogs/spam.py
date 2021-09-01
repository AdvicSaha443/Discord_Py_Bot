import discord
import asyncio
from discord.ext import commands

class Check(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print('Now Checking For Spams!')
    while True:
      await asyncio.sleep(10)
      with open("jsons/msg.txt", "r+") as file:
        file.truncate(0)


  @commands.Cog.listener()
  async def on_message(self, message):
    counter = 0
    with open("jsons/msg.txt","r+") as file:
      for lines in file:
        if lines.strip("\n") == str(message.author.id):
          counter+=1

      file.writelines(f"{str(message.author.id)}\n")
      if counter >= 5:
        mbed = discord.Embed(
          title = "You Have Been Muted In **Skyblock Server** For 1 Minute",
          description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
          color = discord.Color.red()
        )
        mbed2 = discord.Embed(
          title = f"Muted {message.author} For Spamming",
          description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
          color = discord.Color.red()
        )
        mutedRole = discord.utils.get(message.guild.roles, name="Muted")
        await message.author.add_roles(mutedRole ,reason="Spam")
        await message.author.send(embed=mbed)
        await message.channel.send(embed = mbed2)
        await asyncio.sleep(60)
        await message.author.remove_roles(mutedRole)

def setup(client):
  client.add_cog(Check(client))
