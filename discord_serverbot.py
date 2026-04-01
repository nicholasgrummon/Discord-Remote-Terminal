"""server_discord_bot.py - run on host server."""

import os
import subprocess

import discord
from discord.ext import tasks

from utils import bot
from utils import chess
from utils.michelle import Michelle

# ── GLOBALS ────────────────────────────────────────────────────────────────

SERVER_BOT_TOKEN    = os.getenv("MICHELLE_DISCORD_TOKEN")
DONE_MSG            = "done"

status              = {"chess": False, "chat": False, "voice": False}

# ── DISCORD SETUP ──────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
server_bot = discord.Client(intents=intents)

# ── OLLAMA SETUP ───────────────────────────────────────────────────────────

michelle = Michelle()

# ── Events ─────────────────────────────────────────────────────────────────

@server_bot.event
async def on_message(message):
    """Route non-keyword-command messages that begin with $ to the host server terminal"""
    global status
    args = message.content.split()

    # ignore own messages
    if message.author == server_bot.user:
        return
    
    # dispatch shell command messages indicated by "$" leading character
    if message.content[0] == "$":
        shell_command = message.content[1:].strip()
        result = subprocess.run(shell_command, capture_output=True, shell = True)
        output = result.stdout.decode().strip()
        await message.channel.send(output if output else DONE_MSG)
        return

    # dispatch bot command messages indicated by "!" leading character
    if message.content[0] == "!":
        try:
            bot_command = bot.handlers.get(args[0])
            status, response = await bot_command(message, status, args)
            await message.channel.send(response if response else DONE_MSG)

        except Exception:
            await message.channel.send("invalid command")
        finally:
            return

    # handle plaintext messages
    if status["chess"]:
        await chess.play_chess(message, args)
    
    elif status["chat"]:
        michelle.append_chatlog("user", message.content)

        # Send a placeholder to edit into as chunks arrive
        await message.channel.typing()
        response = await michelle.respond()
        await message.channel.send(response)

        if status["voice"]:
            await michelle.speak(response)

        return


# ── Entry point ───────────────────────────────────────────────────────────────

server_bot.run(SERVER_BOT_TOKEN)