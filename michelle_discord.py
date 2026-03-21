"""michelle_discord.py - Michelle is run on host server."""

import os
import subprocess

import discord
from discord.ext import commands

# ── Constants ────────────────────────────────────────────────────────────────

DONE_MSG = "done"
NO_ATTACH_MSG = "no attachment"
MICHELLE_DISCORD_TOKEN = os.getenv("MICHELLE_DISCORD_TOKEN")

# ── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
michelle = discord.Client(intents=intents)

# ── Helpers ───────────────────────────────────────────────────────────────────

async def host_send_worker(channel, self_path, other_path):
    """Recursively send a file or directory tree to a Discord channel.

    Args:
        channel:    The Discord channel to send files to.
        self_path:  Local path of the file or directory to send.
        other_path: Corresponding destination path sent as message content.
    """ 
    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await channel.send(file=file, content=other_path)

    elif os.path.isdir(self_path): 
        for item in os.listdir(self_path):
            await host_send_worker(
                channel,
                os.path.join(self_path, item),
                os.path.join(other_path, item)
            )


# @michelle.command(name="pull")
async def pull(message, host_path, client_path):
    """Pull a file or directory (recursively) from the host server and send as attachment on discord.

    Usage: !pull <host_path> <client_path>
    
    Args:
        host_path:      Valid file or directory path on host server.
        client_path:    Path on client of same type as host_path.
    """
    await host_send_worker(message.channel, host_path, client_path)
    await message.channel.send(DONE_MSG)


# @michelle.command(name="push")
async def push(message, host_filepath):
    """Push an attachment from discord to the host server.

    Usage: !push <client_filepath> <host_filepath>
    
    Args:
        host_filepath:  File path on host server.
    """
    if not message.attachments:
        await message.channel.send(NO_ATTACH_MSG)
        await message.channel.send(DONE_MSG)
        return
    
    for attachment in message.attachments:
        dirpath = os.path.dirname(host_filepath)
        os.makedirs(dirpath, exist_ok=True)
        await attachment.save(host_filepath)
    
    await message.channel.send(DONE_MSG)


# ── Events ────────────────────────────────────────────────────────────────────

@michelle.event
async def on_message(message):
    """Route non-keyword-command messages that begin with $ to the host server terminal"""
    # ignore own messages
    if message.author == michelle.user:
        return
    
    # dispatch shell command messages indicated by $ leading character
    elif message.content[0] == '$':
        shell_command = message.content[1:].strip()
        result = subprocess.run(shell_command, capture_output=True, shell=True)
        output = result.stdout.decode().strip()
        await message.channel.send(output if output else DONE_MSG)
    
    elif message.content.split()[0] == "!ping":
        await message.channel.send("pong!")

    elif message.content.split()[0] == "!pull":
        args = message.content.split()
        if len(args) > 2:
            await pull(message, args[1], args[2])
        else:
            await pull(message, args[1], ".")

    elif message.content.split()[0] == "!push":
        args = message.content.split()
        await push(message, args[1])

    elif message.content.split()[0] == "!hello":
        pass

    elif message.content.split()[0] == "!chess":
        pass

    # ignore plaintext messages
    else:
        pass

# ── Entry point ───────────────────────────────────────────────────────────────

michelle.run(MICHELLE_DISCORD_TOKEN)