"""server_discord_bot.py - run on host server."""

import os
import subprocess

import discord
from discord.ext import tasks

from utils import chess
from utils import michelle

# ── GLOBALS ────────────────────────────────────────────────────────────────

SERVER_BOT_TOKEN        = os.getenv("MICHELLE_DISCORD_TOKEN")
DONE_MSG                = "done"
NO_ATTACH_MSG           = "no attachment"

chess_mode              = False

chat_mode               = False
speaking_mode           = False
message_log             = []

# ── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
server_bot = discord.Client(intents=intents)

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


async def pull(message, host_path, client_path):
    """Pull a file or directory (recursively) from the host server and send as attachment on discord.

    Usage: !pull <host_path> <client_path>
    
    Args:
        host_path:      Valid file or directory path on host server.
        client_path:    Path on client of same type as host_path.
    """
    await host_send_worker(message.channel, host_path, client_path)
    await message.channel.send(DONE_MSG)


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

@server_bot.event
async def on_message(message):
    """Route non-keyword-command messages that begin with $ to the host server terminal"""
    global chess_mode
    global chat_mode, message_log, speaking_mode

    args = message.content.split()

    # ignore own messages
    if message.author == server_bot.user:
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
        if len(args) > 1 and args[1] == "--speak":
            speaking_mode = True

        message_log = await michelle.load_context()
        print(message_log)
        await message.channel.send(michelle.BEGIN_CHAT_MSG)

    elif args[0] == "!chess":
        chess_mode = True
        await chess.begin_chess(message, args)
    
    elif args[0] == "!end":
        if len(args) > 1:
            if args[1] == "chess":
                chess_mode = False
                await chess.end()
                
            elif args[1] == "chat":
                chat_mode = False
                await michelle.end()
        
        else:
            chess_mode = False
            chat_mode = False
            await chess.end()
            await michelle.end(message_log)
        
        await message.channel.send(DONE_MSG)

    # plaintext messages
    elif chess_mode:
        await chess.play_chess(message, args)
    
    elif chat_mode:
        message_log.append({'role': 'user', 'content': message.content})

        # Send a placeholder to edit into as chunks arrive
        await message.channel.typing()
        response = await michelle.respond(message_log)
        message_log.append(response.message)
        await message.channel.send(response.message.content)

        if speaking_mode:
            await michelle.speak(response.message.content)
        return


# ── Entry point ───────────────────────────────────────────────────────────────

server_bot.run(SERVER_BOT_TOKEN)