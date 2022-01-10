from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import asyncio
import chess
import chess.svg
from cairosvg import svg2png

import game

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='$$')

bot.remove_command('help')

sessions: list[game.Session] = []

@bot.event
async def on_ready():
    print("Starting bot..")
    print(f"Bot name: {bot.user.name}, id: {bot.user.id}")

@bot.command()
async def info(ctx: commands.context.Context):
    await ctx.reply(embed=discord.Embed(title="Info", description="Chess bot to play chess with friends! (If you have any)", color=0xFF1111), mention_author=False)

@bot.command()
async def play(ctx: commands.context.Context, other: discord.Member):
    other_id = other.id
    user_id = ctx.author.id
    
    if other_id == bot.user.id:
        await ctx.reply("Playing with AI Chess bot, select bot ELO Rating") 

        await play_ai(ctx, user_id)
        return

    if other.bot:
        await ctx.reply("Cannot play with a bot!", mention_author=False)
        return

    if user_id == other_id:
        await ctx.reply("Cannot play with yourself!", mention_author=False)
        return
    
    await ctx.send(f"<@{other_id}>, <@{user_id}> has challenged you to a chess match, do you agree to play? y or n")
    
    msg = await bot.wait_for('message', check=check(other_id))
    msg_content = msg.content

    if msg_content == "n":
        await ctx.reply("User declined challenge")
        return
    elif msg_content == "y":
        await ctx.reply("User accepted challenge!")

        session = game.Session(ctx, user_id, other_id)
        sessions.append(session)

        await draw_board(ctx, session)
        await play_game(ctx, session)

@bot.command()
async def resign(ctx: commands.context.Context):
    for session in sessions:
        if session.id == ctx.author.id or session.other_id == ctx.author.id:
            session.end()
            sessions.remove(session)                                # TODO: End the game on discord too
            await ctx.send(f"<@{ctx.author.id}> resigned the game")
            return

    await ctx.reply("You are not in a game!", mention_author=False)

async def input(_id: int, ctx: commands.context.Context, session: game.Session):
    await ctx.send(f"<@{_id}>'s turn now")

    msg: discord.message.Message = await bot.wait_for('message', check=check(_id))
    msg_content = msg.content

    move = chess.Move.from_uci(msg_content)

    if not session.board.is_legal(move):
        await msg.reply("Not a legal move")
        raise ValueError

    session.board.push(move)
       
async def play_game(ctx: commands.context.Context, session: game.Session):
    _id = 0

    while True:
        try:
            await input(session.id if _id % 2 == 0 else session.other_id, ctx, session)
            await draw_board(ctx, session)
            _id += 1
        except ValueError:
            pass

async def play_ai(ctx: commands.context.Context, _id: int):
    session = game.Session(ctx, _id, bot.user.id)
    sessions.append(session)

    elo_msg: discord.message.Message = await bot.wait_for('message', check=check(_id))
    elo_content = elo_msg.content

    try:
        elo = int(elo_content, base=10)
    except ValueError:
        await ctx.reply("Not a valid number, exiting game...")
        return

    await elo_msg.reply(f"Selected Bot ELO: {elo}")
    await draw_board(ctx, session)

    __id = 0
    while True:
        try:
            if __id % 2 == 0:
                await input(_id, ctx, session)
            else:
                pass                            # TODO: Make bot ai

            await draw_board(ctx, session)
            __id += 1
        except ValueError:
            pass

def check(_id: int):
    def inner_check(message: commands.context.Context):
        return message.author.id == _id

    return inner_check

async def draw_board(ctx: commands.context.Context, session: game.Session):
    pic = chess.svg.board(session.board, size=300)

    filename = f"chess_{session.id}_{session.other_id}.png"

    svg2png(bytestring=pic, write_to=filename)

    with open(filename, 'rb') as fb:
        pic = discord.File(fb)

        await ctx.send(file=pic)

        os.system(f"rm -rf {filename}")

bot.run(TOKEN)

