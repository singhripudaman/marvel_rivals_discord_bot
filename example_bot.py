import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests

API_URL_BASE = "https://mrapi.org/api/"

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def get_player_id(username):
    r = requests.get(f"{API_URL_BASE}/player-id/{username}")
    return r.json()["id"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)


@bot.command()
async def rivals(ctx, *, content):
    id = get_player_id(content)
    print(id)
    r = requests.get(f"{API_URL_BASE}/player/{id}")
    j = r.json()
    stats = j["stats"]
    level = stats["level"]
    rank = stats["rank"]["rank"]
    hours = stats["total_playtime"]["hours"]
    minutes = stats["total_playtime"]["minutes"]
    embed = discord.Embed(
        title=f"Stats for {j["player_name"]}:",
        description=f"Level: {level}\nRank: {rank}\nHours: {hours}\nMinutes: {minutes}",
        color=discord.Color.green(),
    )

    # embed.set_thumbnail(url=j["avatar_url"])

    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


bot.run(os.environ.get("DISCORD_TOKEN"))
