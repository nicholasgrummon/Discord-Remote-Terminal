'''Run Sam from anywhere. Sam communicates with Michelle, who forwards my Linux terminal'''

import sys
import os
import discord
from discord.ext import commands

# ── Constants ────────────────────────────────────────────────────────────────

DONE_MSG = "done"
COMMAND = " ".join(sys.argv[1:])
SAM_DISCORD_TOKEN = os.getenv('SAM_DISCORD_TOKEN')

# ── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
sam = discord.Client(intents=intents)

# ── Helpers ───────────────────────────────────────────────────────────────────

async def client_send_worker(channel, self_path, other_path):
    """Recursively send a file or directory tree to a Discord channel.

    Args:
        channel:    The Discord channel to send files to.
        self_path:  Local path of the file or directory to send.
        other_path: Corresponding destination path sent as message content.
    """ 
    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await channel.send(file=file, content=f"!push {other_path}")

    elif os.path.isdir(self_path): 
        for item in os.listdir(self_path):
            await client_send_worker(
                channel,
                "/".join([self_path, item]),
                "/".join([other_path, item])
            )

# ── Events ────────────────────────────────────────────────────────────────────

@sam.event
async def on_ready():
    channel_id = 1483247531235479665
    channel = sam.get_channel(channel_id)

    if sys.argv[1] == "push":
        self_basepath = sys.argv[2]
        other_basedirpath = sys.argv[3]
        await client_send_worker(channel, self_basepath, other_basedirpath)

    elif sys.argv[1] == "pull":
        await channel.send("!" + COMMAND)
    
    else:
        await channel.send("$" + COMMAND)


@sam.event
async def on_message(message):
    # ignore own messages
    if message.author == sam.user:
        return
    
    # close client if transmission done
    elif message.content == DONE_MSG:
        await sam.close()

    # save files received from pull
    elif message.attachments:
        for attachment in message.attachments:
            filepath = message.content
            dirpath = os.path.dirname(filepath)

            os.makedirs(dirpath, exist_ok=True)
            await attachment.save(filepath)


# run the bot with your token
sam.run(SAM_DISCORD_TOKEN)