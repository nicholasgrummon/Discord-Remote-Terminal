import os
import discord
import subprocess

from utils import michelle
from utils import chess

# ── Commands ──────────────────────────────────────────────────────────────

async def ping(message, status, args=None):
    return status, "pong!"


async def pull(message, status, args):

    self_path = args[1]
    other_path = args[2] if len(args) > 2 else "."

    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await message.channel.send(file=file, content=other_path)

    elif os.path.isdir(self_path):
        for item in os.listdir(self_path):
            args[1] = os.path.join(self_path, item)
            args[2] = os.path.join(other_path, item)
            await pull(message, status, args)
    
    return status, None


async def push(message, status, args):
    host_filepath = args[1]
    if not message.attachments:
        return status, "no attachment"
    
    for attachment in message.attachments:
        dirpath = os.path.dirname(host_filepath)
        os.makedirs(dirpath, exist_ok=True)
        await attachment.save(host_filepath)
    
    return status, None


async def begin_chat(message, status, args):
    if not status["chat"]:
        status["chat"] = True
        await michelle.load_context()
        return status, await michelle.begin_chat()
    
    return status, "chat already active"


async def begin_chess(message, status, args):
    if not status["chess"]:
        status["chess"] = True
        return status, await chess.begin_chess(message, args)
    
    return status, "chess already active"


async def end(message, status, args):
    if len(args) > 1:
        match args[1]:
            case "chess": status["chess"] = False; await chess.end()
            case "chat": status["chat"] = False; await michelle.end()
    
    else:
        status = {"chess": False, "chat": False, "voice":False}
        await chess.end()
        await michelle.end()
    
    return status, None
    

# ── Handlers ──────────────────────────────────────────────────────────────
handlers = {
    "!ping": ping,
    "!pull": pull,
    "!push": push,
    "!hello": begin_chat,
    "!chess": begin_chess,
    "!end": end
}