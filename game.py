from discord.ext import commands
import chess

class Session:
    def __init__(self, ctx: commands.context.Context, user_id: int, other_id: int):
        self.ctx = ctx
        self.id = user_id
        self.other_id = other_id

        self.board = chess.Board()

