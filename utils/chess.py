from stockfish import Stockfish
import random

# ── GLOBALS ────────────────────────────────────────────────────────────────
chess_mode              = False
STOCKFISH               = Stockfish("/usr/games/stockfish")
CHESS_START_MSG         = "Let's play!"
BAD_MOVE_MSG            = "illegal move"
SHOW_BRD_MSG            = "show"

# ── UTILS ────────────────────────────────────────────────────────────────

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
        return CHESS_START_MSG + " You start with white."

    elif color == "b" or color == "black":
        sf_move = STOCKFISH.get_best_move()
        STOCKFISH.make_moves_from_current_position([sf_move])
        return CHESS_START_MSG + f" I play {sf_move}:"


async def play_chess(user_move):
    if user_move == "show":
        return STOCKFISH.get_board_visual()

    elif STOCKFISH.is_move_legal(user_move):
        STOCKFISH.make_moves_from_current_position([user_move])
        stockfish_move = STOCKFISH.get_best_move()
        STOCKFISH.make_moves_from_current_position([stockfish_move])
        return stockfish_move

    else:
        return BAD_MOVE_MSG


async def end():
    STOCKFISH.send_quit_command()
    return