import os
import discord

from utils import chess
from utils.status import Status
from michelle import Michelle

# ── GLOBALS ────────────────────────────────────────────────────────────────

CHAT_MODEL = "llama3.1:8b"

# ── Commands ──────────────────────────────────────────────────────────────

async def ping(message, state, args=None):
    return "pong!", state


async def pull(message, state, args):

    self_path = args[1]
    other_path = args[2] if len(args) > 2 else "."

    if os.path.isfile(self_path):
        file = discord.File(self_path)
        await message.channel.send(file=file, content=other_path)

    elif os.path.isdir(self_path):
        for item in os.listdir(self_path):
            args[1] = os.path.join(self_path, item)
            args[2] = os.path.join(other_path, item)
            await pull(message, state, args)
    
    return None, state


async def push(message, state, args):
    host_filepath = args[1]
    if not message.attachments:
        return "No attachment", state
    
    for attachment in message.attachments:
        dirpath = os.path.dirname(host_filepath)
        os.makedirs(dirpath, exist_ok=True)
        await attachment.save(host_filepath)
    
    return None, state


async def begin_chat(message, state, args):
    if not state.chat_flag:
        state.chat_flag = True
        state.chat_model = Michelle(CHAT_MODEL)
        await state.chat_model.start()
        return "Let's chat", state
    
    return "Chat already active", state


async def begin_chess(message, state, args):
    if not state.chess_flag:
        state.chess_flag = True
        response = await chess.begin_chess(message, args)
        return response, state
    
    return "Chess already active", state


async def end(message, state, args):
    if len(args) > 1:
        match args[1]:
            case "chess":
                state.chess_flag = False
                await chess.end()
            case "chat":
                state.chat_flag = False
                await state.chat_model.__del__()
    
    else:
        await state.clear()
    
    return None, state
    

# ── Handlers ──────────────────────────────────────────────────────────────
handlers = {
    "!ping": ping,
    "!pull": pull,
    "!push": push,
    "!hello": begin_chat,
    "!chess": begin_chess,
    "!end": end
}