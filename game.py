from discord.ext import commands
import chess

class Session:
    def __init__(self, ctx: commands.context.Context, user_id: int, other_id: int):
        self.ctx = ctx
        self.id = user_id
        self.other_id = other_id

        self.board = chess.Board()

        self.running = True

    def end(self):
        self.running = False

    def is_active(self) -> bool:
        return self.running

