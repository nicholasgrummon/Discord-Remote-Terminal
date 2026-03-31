import os
import asyncio
import subprocess
import ollama

# ── GLOBALS ────────────────────────────────────────────────────────────────
chat_mode               = False
BEGIN_CHAT_MSG          = "Let's chat!"
OLLAMA_MODEL            = "Michelle_v2"
ONLOAD_PROMPT           = "I know the following from past conversations: "
CONDENSER_MODEL         = "llama3.1:8b"
CONDENSE_MSG            = "Summarize all message history. Be as brief as possible. Always specify the subject."
CHATLOG_PATH            = "outs/chat_log.txt"

speaking_mode           = False
VOICE                   = "tts/en_US-libritts_r-medium"

# ── UTILS ────────────────────────────────────────────────────────────────

async def begin_chat():
    return BEGIN_CHAT_MSG

async def load_context():
    if os.path.exists(CHATLOG_PATH):
        with open(CHATLOG_PATH, "r") as file:
            inject_memory_msg = ONLOAD_PROMPT + file.read()
            return {"role": "assistant", "content": inject_memory_msg}


async def respond(message_log):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: ollama.chat(model=OLLAMA_MODEL, messages=message_log)
    )


async def speak(script, volume=0.2):
    script = script.replace('"', '\\"').replace("'", "\\'") # remove any unterminated quotes
    speak_command = f"echo {script} | python -m piper -m {VOICE} --volume {volume} --sentence-silence 0.5 --length-scale 1.2"
    print(speak_command)
    subprocess.run(speak_command, shell=True)


async def condense_context(message_log):
    message_log.append({"role": "user", "content": CONDENSE_MSG})

    loop = asyncio.get_event_loop()
    condensed_log = await loop.run_in_executor(
        None,
        lambda: ollama.chat(model=CONDENSER_MODEL, messages=message_log)
    )

    message_log = condensed_log.message
    os.makedirs("outs", exist_ok=True)
    with open(CHATLOG_PATH, "w") as file:
        file.write(message_log.content)
    
    return


async def end(message_log):
    global chat_mode, speaking_mode
    chat_mode = False
    speaking_mode = False
    await condense_context(message_log)
    return

