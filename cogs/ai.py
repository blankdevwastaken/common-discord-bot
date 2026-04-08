import json
from socket import CAN_BCM_TX_ANNOUNCE
from openai import OpenAI
import discord 
from discord.ext import commands 
from utils import check.is_mod
from config import GROQ_API_KEY
from config import 
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)
class AI(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

@commands.command(name="ask")
async def ask(ctx: commands.Context, *, question: str):
    if ctx.channel.id != 1491570828410622063
        await ctx.reply("Please ask questions in the #ai channel.")
        return
    response = ask_groq(question)
    await ctx.reply(response)    
def ask_groq(question: str) -> str:
    response = client.chat.completions.create(
        model="groq-1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for the commonluke discord server your personality is the primagen all text outputs must be like the primeagen also only respond if a user is asking a question or is talking directly to you otherwise ignore the message and do not respond."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content.strip()    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
