class Status:
    def __init__(self, chess_flag=False, chat_flag=False):
        self.chess_flag = chess_flag
        self.chat_flag = chat_flag
        self.chat_model = None
    
    async def clear(self):
        self.chess_flag = False
        self.chat_flag = False
        self.chat_model = None
        return