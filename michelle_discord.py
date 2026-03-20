'''Michelle runs commands on my remote Linux server to allow terminal access from anywhere'''

import discord
from discord.ext import commands
import subprocess
import os

DONE_MSG = "done"

# create instance of Bot class
intents = discord.Intents.default()
intents.message_content = True
michelle = commands.Bot(command_prefix='!', intents=intents)

# helper function
async def send_worker(message, self_path, other_path):
    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await message.channel.send(file=file, content=other_path)

    elif os.path.isdir(self_path): 
        for item in os.listdir(self_path):
            await send_worker(message, os.path.join(self_path, item), os.path.join(other_path, item))


# # define a command
# @michelle.command(name='ping')
# async def ping(ctx):
#     await ctx.send('pong')

# on message
@michelle.event
async def on_message(message):
    # ignore own messages
    if message.author == michelle.user:
        return

    # regular terminal command
    elif message.content[0] == '$':
        command = message.content[1:]
        out = subprocess.run(command, capture_output=True, shell=True)
        try:
            # forward terminal output
            await message.channel.send(out.stdout.decode())
        except Exception:
            # forward confirmation message
            await message.channel.send(DONE_MSG)
        return
    
    # keyword discord command
    elif message.content[0] == '!':
        discord_command = message.content[1:]

        # pull keyword
        if discord_command[0:4] == "pull":  # !pull bin container
            self_basepath = discord_command.split(" ")[1] # bin
            other_basepath = discord_command.split(" ")[2] # container
            await send_worker(message, self_basepath, other_basepath)
            await message.channel.send(DONE_MSG)

        elif discord_command[0:4] == "push":
            try:
                for attachment in message.attachments:
                    filepath = message.content.split(" ")[-1]
                    dirpath = os.path.dirname(filepath)

                    if not os.path.exists(dirpath):
                        os.makedirs(dirpath)

                    with open(filepath, 'w') as _:
                        pass

                    await attachment.save(filepath)
                    await message.channel.send(DONE_MSG)

            except Exception:
                print(Exception)
                await message.channel.send("need attachment")


# run the bot with your token
MICHELLE_DISCORD_TOKEN = os.getenv('MICHELLE_DISCORD_TOKEN')
michelle.run(MICHELLE_DISCORD_TOKEN)