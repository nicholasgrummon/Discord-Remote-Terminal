"""server_discord_bot.py - run on host server."""

import os
import subprocess

import discord
from discord.ext import tasks

from utils import commands
from utils import chess
from utils.status import Status
from michelle import Michelle

# ── GLOBALS ────────────────────────────────────────────────────────────────

SERVER_BOT_TOKEN    = os.getenv("MICHELLE_DISCORD_TOKEN")
DONE_MSG            = "done"

state              = Status(chess_flag=False, chat_flag=False)

# ── DISCORD SETUP ──────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
server_bot = discord.Client(intents=intents)

# ── Events ─────────────────────────────────────────────────────────────────

@server_bot.event
async def on_message(message):
    """Route non-keyword-command messages that begin with $ to the host server terminal"""
    global state
    args = message.content.split()

    # ignore own messages
    if message.author == server_bot.user:
        return
    
    # Send typing bubbles
    await message.channel.typing()

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
            bot_command = commands.handlers.get(args[0])
            response, state = await bot_command(message, state, args)
            await message.channel.send(response if response else DONE_MSG)

        except Exception as e:
            print(e)
            await message.channel.send("invalid command")
        finally:
            return

    # handle plaintext messages
    if state.chess_flag:
        await message.channel.send(await chess.play_chess(str(args[0]).lower()))
    
    elif state.chat_flag:
        await state.chat_model.add_context("user", message.content)
        response = await state.chat_model.chat()
        await message.channel.send(response.message.content)


# ── Entry point ───────────────────────────────────────────────────────────────

server_bot.run(SERVER_BOT_TOKEN)