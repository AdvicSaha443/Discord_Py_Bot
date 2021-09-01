import discord
import asyncio
import json
from discord.ext import commands
from better_profanity import profanity

class Check(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print('Now Checking Messages!')

  profanity.load_censor_words_from_file('jsons/badwords.txt')

  @commands.Cog.listener()
  async def on_message(self, message):
    if not message.author.bot:
      if profanity.contains_profanity(message.content):
        mbed = discord.Embed(
          title = str(message.author) + ' ' + 'Has Been Warned For Using A Bad Word',
          description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
          color = discord.Color.red()
        )
        await message.delete()
        await message.channel.send(embed = mbed)
        await message.author.send("You Can't Use That Word Here!")
        return
      else:
        if message.guild is not None:
          if not message.content.startswith('?'):
            with open("jsons/mainBank.json", "r") as f:
              users = json.load(f)

            SB = []
            SBROLE = discord.utils.get(message.guild.roles, name="SB-DOUBLE")

            for member in message.guild.members:
              if SBROLE in member.roles:
                  SB.append(member.name + '#' + member.discriminator)

            if str(message.author) in SB:
              users[str(message.author.id)]["bank"] += 2000
            else:
              users[str(message.author.id)]["bank"] += 100

            with open("jsons/mainBank.json", "w") as f:
              json.dump(users, f)
          else: 
            return
        else:
          return

def setup(client):
  client.add_cog(Check(client))

