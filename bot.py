import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests
import sqlite3

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tree = bot.tree

# Initialize SQLite
conn = sqlite3.connect("usernames.db")
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS user_map (
        discord_id TEXT PRIMARY KEY,
        game_username TEXT NOT NULL
    )
"""
)
conn.commit()


def get_username(user_id):
    c.execute("SELECT game_username FROM user_map WHERE discord_id = ?", (user_id,))
    result = c.fetchone()
    return result


@tree.command(name="setusername", description="Set a member's in-game username")
@app_commands.describe(
    member="The Discord member", in_game_username="The in-game username"
)
async def setusername(
    interaction: discord.Interaction, member: discord.Member, in_game_username: str
):
    """Set a member's in-game username.

    This command sets the in-game username associated with a given Discord member.
    The username is stored in a SQLite database, and can be retrieved with the
    `getusername` command.

    Note that the username is case-sensitive, so "JohnDoe" and "johndoe" are
    considered different usernames.

    Parameters:
    - interaction (discord.Interaction): The interaction object representing the command invocation.
    - member (discord.Member): The Discord member whose username is to be set.
    - in_game_username (str): The in-game username to set.

    Sends:
    - A message indicating that the username has been set successfully.
    """
    user_id = str(member.id)
    with conn:
        conn.execute(
            "REPLACE INTO user_map (discord_id, game_username) VALUES (?, ?)",
            (user_id, in_game_username),
        )
    await interaction.response.send_message(
        f"{member.mention}'s in-game username has been set to `{in_game_username}` by {interaction.user.mention}.",
        ephemeral=False,
    )


@tree.command(name="getusername", description="Get a member's in-game username")
@app_commands.describe(member="The Discord member (leave empty to get your own)")
async def getusername(interaction: discord.Interaction, member: discord.Member = None):
    """
    Retrieve a member's in-game username.

    This command retrieves the in-game username associated with a given Discord member.
    If no member is specified, it retrieves the username of the user who invoked the command.
    The username is fetched from a SQLite database where it has been previously stored using
    the `setusername` command.

    Parameters:
    - interaction (discord.Interaction): The interaction object representing the command invocation.
    - member (discord.Member, optional): The Discord member whose username is to be retrieved. Defaults to the invoking user.

    Sends:
    - A message indicating the member's in-game username if it exists.
    - A message indicating that the member has not set an in-game username if it does not exist.
    """

    member = member or interaction.user
    user_id = str(member.id)
    result = get_username(user_id)
    if result:
        await interaction.response.send_message(
            f"{member.mention}'s in-game username is `{result[0]}`."
        )
    else:
        await interaction.response.send_message(
            f"{member.mention} has not set an in-game username yet."
        )


@tree.command(
    name="roast", description="Roast a Marvel Rivals player based on their stats!"
)
@app_commands.describe(member="The player's discord tag")
async def roast(interaction: discord.Interaction, member: discord.Member):
    """
    Roast a Marvel Rivals player based on their in-game stats.

    This command generates a humorous roast for a given Marvel Rivals player,
    using their in-game statistics. The player's username is fetched from the
    SQLite database. If the username exists, the bot retrieves the player's
    stats from an external API and generates a roast using the OpenAI API.

    Parameters:
    - interaction (discord.Interaction): The interaction object representing
      the command invocation.
    - member (discord.Member): The Discord member whose in-game stats will be used
      for generating the roast.

    Sends:
    - A playful and humorous roast message embedded in an embed object.
    - A message indicating that the member has not set an in-game username if it does not exist.
    """

    await interaction.response.defer(thinking=True)
    user_id = str(member.id)

    result = get_username(user_id)
    if result:
        username = result[0]
    else:
        await interaction.followup.send(
            content=f"{member.mention} has not set an in-game username yet."
        )
        return

    response = requests.get(
        f"{API_BASE_URL}/api/get_player_data?mr_username={username}"
    ).json()

    # Create the prompt for ChatGPT
    prompt = f"""You are a witty and sharp game stats analyst who roasts players with humor based on their in-game stats in marvel rivals.
                Roast the player \"{username}\" based on this player data:

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

    embed = discord.Embed(
        title=f"🔥 Roast for {username} 🔥",
        description=roast,
        color=discord.Color.red(),
    )

    await interaction.followup.send(content=member.mention, embed=embed)


@tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    """
    Respond with the bot's latency.

    This command sends a message to the Discord channel indicating the current latency
    of the bot in milliseconds. It is useful for checking the responsiveness of the bot.

    Parameters:
    - interaction (discord.Interaction): The interaction object representing the command invocation.

    Sends:
    - A message displaying "Pong!" followed by the latency in milliseconds.
    """

    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")


@bot.event
async def on_ready():
    await tree.sync()
    print(f"We have logged in as {bot.user} and synced commands!")


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_TOKEN"))
