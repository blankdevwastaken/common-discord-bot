import json

import discord 
from discord.ext import commands 
from utils import check.is_mod

class ActiveMember(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    # ── Active Member Tracking and checks if prestige is present and then applies it. 
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        with open("data/data.json5", "r") as f:
            data = json.load(f)
        if message.author.bot:
            return
        user_id = str(message.author.id)
        if user_id not in data:
            data[user_id] = {
                "messages": 0,
                "last_active": None
            }
        
        data[user_id]["messages"] += 1
        if data[user_id]["prestige_count"] > 0:
            prestige_multiplier = data[user_id]["prestige_count"] * 0.5
            data[user_id]["messages"] += prestige_multiplier
        with open("data/data.json5", "w") as f:
            json.dump(data, f, indent=4)
    # Pulls the top 10 people with the most messages
    @commands.hybrid_command(name="leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        with open("data/data.json5", "r") as f:
            data = json.load(f)
        
        top_10 = sorted(data.items(), key=lambda x: x[1]["messages"], reverse=True)[:10]
        
        leaderboard_text = "**Top 10 Active Members**\n"
        for index, (user_id, user_data) in enumerate(top_10, 1):
            leaderboard_text += f"{index}. <@{user_id}> - {user_data['messages']} messages\n"
        
        await ctx.send(leaderboard_text)
    # Lets the user check their messages via pulling the data from the DB/json
    @commands.hybrid_command(name="mymessages", aliases=["level", "stats", "messages"])
    async def mymessages(self, ctx: commands.Context):
        with open("data/data.json5", "r") as f:
            data = json.load(f)
        
        user_id = str(ctx.author.id)
        messages = data.get(user_id, {}).get("messages", 0)
        
        await ctx.send(f"{ctx.author.mention}, you have sent {messages} messages!")
        
    # force resets a members messages 
    @commands.hybrid_command(name="resetmessages")
    @check.is_mod
    async def resetmessages(self, ctx: commands.Context, member: discord.Member):
        with open("data/data.json5", "r") as f:
            data = json.load(f)
        
        user_id = str(member.id)
        if user_id in data:
            data[user_id]["messages"] = 0
            
            with open("data/data.json5", "w") as f:
                json.dump(data, f, indent=4)
            
            await ctx.send(f"{member.mention}'s message count has been reset.")
        else:
            await ctx.send(f"{member.mention} has no recorded messages.")
    # Resets the users message count and adds a prestige level 
    @commands.hybrid_command(name="prestige")
    async def prestige(self, ctx: commands.Context):
        with open("data/data.json5", "r") as f:
            data = json.load(f)
        
        user_id = str(ctx.author.id)
        messages = data.get(user_id, {}).get("messages", 0)
        
        if messages >= 500:
            data[user_id]["messages"] = 0
            data[user_id]["prestige_count"] = data[user_id].get("prestige_count", 0) + 1
            with open("data/data.json5", "w") as f:
                json.dump(data, f, indent=4)
            
            await ctx.send(f"{ctx.author.mention}, you have prestiged! Your message count has been reset and you have a 1.5x prestige multiplier for the next 500 messages. You have prestiged {data[user_id]['prestige_count']} times.")
        else:
            await ctx.send(f"{ctx.author.mention}, you need at least 500 messages to prestige. You currently have {messages} messages.")
        
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ActiveMember(bot))
