"""michelle_discord.py - Michelle is run on host server."""

import os
import subprocess

import discord
from discord.ext import commands

# ── Plug-Ins ────────────────────────────────────────────────────────────────

from stockfish import Stockfish
import random

import ollama

# ── GLOBALS ────────────────────────────────────────────────────────────────

DONE_MSG                = "done"
NO_ATTACH_MSG           = "no attachment"
MICHELLE_DISCORD_TOKEN  = os.getenv("MICHELLE_DISCORD_TOKEN")

chess_mode              = False
STOCKFISH               = Stockfish("/usr/games/stockfish")
CHESS_START_MSG         = "Let's play!"
BAD_MOVE_MSG            = "illegal move"
SHOW_BRD_MSG            = "show"

chat_mode               = False
BEGIN_CHAT_MSG          = "Let's chat!"

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

# ── Plug-In Apps ──────────────────────────────────────────────────────────

async def begin_chess(message, args):
    # assign performance rating
    performance = args[args.index("-p") + 1] if "-p" in args else 20
    STOCKFISH.update_engine_parameters({"Skill Level": int(performance)})
    STOCKFISH.make_moves_from_start()

    # assign color
    color = args[args.index("-c") + 1] if "-c" in args else "w"
    if color == "r" or color == "random":
        color = ["w", "b"][random.randint(0,1)]

    if color == "w" or color == "white":
        await message.channel.send(CHESS_START_MSG + " You start with white.")

    elif color == "b" or color == "black":
        sf_move = STOCKFISH.get_best_move()
        STOCKFISH.make_moves_from_current_position([sf_move])
        await message.channel.send(CHESS_START_MSG + f" I play {sf_move}:")

# ── Events ────────────────────────────────────────────────────────────────────

@michelle.event
async def on_message(message):
    """Route non-keyword-command messages that begin with $ to the host server terminal"""
    global chess_mode
    global chat_mode
    args = message.content.split()

    # ignore own messages
    if message.author == michelle.user:
        return
    
    # dispatch shell command messages indicated by $ leading character
    elif message.content[0] == '$':
        shell_command = message.content[1:].strip()
        result = subprocess.run(shell_command, capture_output=True, shell=True)
        output = result.stdout.decode().strip()
        await message.channel.send(output if output else DONE_MSG)
    
    elif args[0] == "!ping":
        await message.channel.send("pong!")

    elif args[0] == "!pull":
        if len(args) > 2:
            await pull(message, args[1], args[2])
        else:
            await pull(message, args[1], ".")

    elif args[0] == "!push":
        args = message.content.split()
        await push(message, args[1])

    elif args[0] == "!hello":
        chat_mode = True
        await message.channel.send(BEGIN_CHAT_MSG)

    elif args[0] == "!chess":
        chess_mode = True
        await begin_chess(message, args)
    
    elif args[0] == "!end":
        chess_mode = False
        STOCKFISH.send_quit_command()

        chat_mode = False
        await message.channel.send(DONE_MSG)

    # plaintext messages
    elif chess_mode:
        if args[0] == "!show":
            await message.channel.send(STOCKFISH.get_board_visual())

        elif STOCKFISH.is_move_legal(args[0]):
            STOCKFISH.make_moves_from_current_position([args[0]])
            sf_move = STOCKFISH.get_best_move()
            STOCKFISH.make_moves_from_current_position([sf_move])

            await message.channel.send(sf_move)

        else:
            await message.channel.send(BAD_MOVE_MSG)
    
    elif chat_mode:
        response = ollama.chat(model="Michelle_v0", messages=[{'role': 'user', 'content':message.content}])
        await message.channel.send(response.message.content)
        return


# ── Entry point ───────────────────────────────────────────────────────────────

michelle.run(MICHELLE_DISCORD_TOKEN)