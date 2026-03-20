'''Run Sam from anywhere. Sam communicates with Michelle, who forwards my Linux terminal'''

import sys
import os
import discord
from discord.ext import commands

SPECIAL_COMMANDS = ["push", "pull", "ping"]
DONE_MSG = "done"

# read command for sam to pass
command = " ".join(sys.argv[1:])

# create instance of Bot class
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
sam = commands.Bot(command_prefix='', intents=intents)

async def send_worker(channel, self_path, other_path):
    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await channel.send(file=file, content=f"!push {other_path}")

    elif os.path.isdir(self_path): 
        for item in os.listdir(self_path):
            await send_worker(channel, "/".join([self_path, item]), "/".join([other_path, item]))


# on ready
@sam.event
async def on_ready():
    channel_id = 1483247531235479665
    channel = sam.get_channel(channel_id)

    if sys.argv[1] == "push":
        self_basepath = sys.argv[2]
        other_basedirpath = sys.argv[3]
        await send_worker(channel, self_basepath, other_basedirpath)

    elif sys.argv[1] == "pull":
        await channel.send("!" + command)
    
    else:
        await channel.send("$" + command)


@sam.event
async def on_message(message):
    # ignore own messages
    if message.author == sam.user:
        return
    
    if message.content == DONE_MSG:
        await sam.close()

    else:
        try:
            for attachment in message.attachments:
                filepath = message.content
                dirpath = os.path.dirname(filepath)

                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                with open(filepath, 'w') as _:
                    pass

                await attachment.save(filepath)
        
        except Exception:
            pass

# run the bot with your token
SAM_DISCORD_TOKEN = os.getenv('MICHELLE_DISCORD_TOKEN')
sam.run(SAM_DISCORD_TOKEN)