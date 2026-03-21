## Discord Remote Terminal

### About
This project makes use of discord bots to provide terminal access to a host server. It accomplishes the same functionality as port forwarding, but makes use of the intermediary discord platform to avoid exposing the host server to the internet. Instead, a server bot (Michelle) and a client bot (Sam) communicate with each other in a private discord channel to convey terminal commands from a client to the host server and to relay stdout back to the client. Special push/pull commands are additionally implemented to enable whole-directory replication on the client - similar to git usage except that direct modification of host server files is allowed.

### Usage and Functionality
The application makes use of two discord bots:
<br>
1. Michelle: Operates on the host server. Run via `$ ./runner.sh`.Executes messages from discord as commands on the host server terminal and returns any stdout back to the discord channel. Accepts special commands "ping", "pull", "push", "hello" (TODO), and "chess" (TODO) as follows:
   1. `!ping` returns "pong!"
   2. `!pull <host_path> <client_path>` enters subroutine to send every file at or under location `host_path` as an attachment or series of attachments. Sends `DONE_MESSAGE` in separate message at end. `host_path` may be file or directory, `client_path` must be same type.
   3. `!push <host_filepath> [!has attachment]` saves the attachment at location `host_filepath`. Responds with `DONE_MSG` (no stdout).
   4. `!hello` starts ollama module to communicate with Michelle as a normal chat assistant (TODO).
   5. `!chess` starts stockfish module to play chess with Michelle in chat (TODO).

<br>

2. Sam: Operates locally on client, OS agnostic (TODO remove discord.py dependency). Run via `$ python sam_discord.py <command> [options]` or set alias via `doskey sam=python <absolute/filepath/to/sam_discord.py> $*` in Windows or `echo "export sam=python <absolute/filepath/to/sam_discord.py> $*" >> ~/.bashrc` in Linux. Passes `<command> [options]` directly to discord and prints any received messages. Closes execution when `DONE_MSG` is received. Has special routines for commands "push" as follows:
   1. `sam push <client_path> <host_path>` enters subroutine to send every file at or under location `client_path` as an attachment.

### Discord Setup
To create new discord bots:
1. Go to https://discord.com/developers/home, sign in, and select Create > build a bot for your server or community
2. Check box under Bot > Bot Permissions > Administrator
3. Ensure sliders are selected as desired to enable messaging, etc
4. Select Bot > Reset Token and copy token
5. In OAuth2 tab, copy ClientID
6. In OAuth2 tab, go to generated url to add bot to server

Install python dependencies to host bots as follows: <br>
`$ python -m pip install -U discord.py`