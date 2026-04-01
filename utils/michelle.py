import os
import asyncio
import subprocess
import ollama

class Michelle:
    def __init__(self):
        self.OLLAMA_MODEL       = "Michelle_v2"
        self.BEGIN_CHAT_MSG     = "Let's chat!"
        self.CHATLOG_PATH       = "outs/chat_log.txt"
        self.chatlog            = []

        self.speaking_mode      = False
        self.SPEAKING_MODEL     = "llama3.2:1b"
        self.VOICE              = "tts/en_US-libritts_r-medium"

        self.CONDENSER_MODEL    = "llama3.1:8b"
        self.CONDENSE_MSG       = "Summarize all message history. Be as brief as possible. Always specify the subject."
        self.ONLOAD_PROMPT      = "I know the following from past conversations: "


    async def clear_chatlog(self):
        self.chatlog = []
    

    async def append_chatlog(self, role, message):
        self.chatlog.append({"role": role, "content": message})


    async def begin_chat(self):
        return self.BEGIN_CHAT_MSG


    async def load_context(self):
        if os.path.exists(self.CHATLOG_PATH):
            with open(self.CHATLOG_PATH, "r") as file:
                inject_memory_msg = self.ONLOAD_PROMPT + file.read()
                self.clear_chatlog()
                self.append_chatlog("assistant", inject_memory_msg)


    async def respond(self, memory=True):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ollama.chat(model=self.OLLAMA_MODEL, messages=self.chatlog)
        )

        self.append_chatlog("assistant", response.message.content) if memory else None
        return response.message.content


    async def speak(self, script, volume=0.2):
        script = script.replace('"', '\\"').replace("'", "\\'") # remove any unterminated quotes
        speak_command = f"echo {script} | python -m piper -m {self.VOICE} --volume {volume} --sentence-silence 0.5 --length-scale 1.2"
        subprocess.run(speak_command, shell=True)


    async def condense_context(self, message_log):
        self.append_chatlog("user", self.CONDENSE_MSG)

        loop = asyncio.get_event_loop()
        chat_summary = await loop.run_in_executor(
            None,
            lambda: ollama.chat(model=self.CONDENSER_MODEL, messages=self.chatlog)
        )

        os.makedirs("outs", exist_ok=True)
        with open(self.CHATLOG_PATH, "w") as file:
            file.write(chat_summary.message)


    async def end(self, message_log):
        global chat_mode, speaking_mode
        chat_mode = False
        speaking_mode = False
        await self.condense_context(message_log)
        return