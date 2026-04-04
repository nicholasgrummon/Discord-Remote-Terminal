import os
import asyncio
import subprocess
import ollama

OLLAMA_MODEL       = "Michelle_v2"
BEGIN_CHAT_MSG     = "Let's chat!"
CHATLOG_PATH       = "outs/chat_log.txt"
chatlog            = []

SPEAKING_MODEL     = "llama3.2:1b"
VOICE              = "tts/en_US-libritts_r-medium"

CONDENSER_MODEL    = "llama3.1:8b"
CONDENSE_MSG       = "Summarize all chat history as concisely as possible. Use the following buckets:\nUser:\n[facts about user - name, occupation, etc]\n[user's moods]\n[user's upcoming plans]\nMyself (Michelle):\n[facts about Michelle]\n[moods of Michelle]\n[Michelle's current tasks]"
ONLOAD_PROMPT      = "I know the following from past conversations: "


async def clear_chatlog():
    global chatlog
    chatlog = []


async def append_chatlog(role, message):
    global chatlog
    chatlog.append({"role": role, "content": message})


async def begin_chat():
    return BEGIN_CHAT_MSG


async def load_context():
    global chatlog
    if os.path.exists(CHATLOG_PATH):
        with open(CHATLOG_PATH, "r") as file:
            inject_memory_msg = ONLOAD_PROMPT + file.read()
    
        await clear_chatlog()
        await append_chatlog("assistant", inject_memory_msg)


async def respond(memory=True):
    global chatlog
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ollama.chat(model=OLLAMA_MODEL, messages=chatlog)
    )

    await append_chatlog("assistant", response.message.content) if memory else None
    return response.message.content


async def speak(script, volume=0.2):
    script = script.replace('"', '\\"').replace("'", "\\'") # remove any unterminated quotes
    speak_command = f"echo {script} | python -m piper -m {VOICE} --volume {volume} --sentence-silence 0.5 --length-scale 1.2"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: subprocess.run(speak_command, shell=True)
    )
    


async def condense_context():
    global chatlog
    await append_chatlog("user", CONDENSE_MSG)

    loop = asyncio.get_event_loop()
    chat_summary = await loop.run_in_executor(
        None,
        lambda: ollama.chat(model=CONDENSER_MODEL, messages=chatlog)
    )

    os.makedirs("outs", exist_ok=True)
    with open(CHATLOG_PATH, "w") as file:
        file.write(chat_summary.message.content)


async def end():
    await condense_context()