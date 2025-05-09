import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests

API_URL_BASE = "http://marvels_api.hamood.dev"

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
async def roast(ctx, *, content):

    username = content
    await ctx.reply("Let me cook...")
    await ctx.message.channel.typing()

    response = requests.get(
        f"{API_URL_BASE}/api/get_player_data?mr_username={username}"
    ).json()

    # Create the prompt for ChatGPT
    prompt = f"""You are a witty and sharp game stats analyst who roasts players with humor based on their in-game stats in marvel rivals.
                Roast the player "{username}" based on this player data:

                {response}

                The roast should be funny, casual, and slightly savage — but not toxic or offensive. Format it like a playful Discord message.

                make last sentence a small tip
                """

    # Call OpenAI (gpt-4 or gpt-3.5-turbo works fine)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in roasting game players humorously.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.8,  # higher temp makes it spicier
    )

    roast = response.choices[0].message.content

    # Create the embed
    embed = discord.Embed(
        title=f"🔥 Roast for {username} 🔥",
        description=roast,
        color=discord.Color.red(),
    )

    # Optional: If you have avatar URLs in player_data or elsewhere
    # embed.set_thumbnail(url=player_data.get("avatar_url", DEFAULT_IMAGE))

    await ctx.send(content=ctx.author.mention, embed=embed)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


bot.run(os.environ.get("DISCORD_TOKEN"))
