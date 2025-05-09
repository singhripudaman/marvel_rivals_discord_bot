# Marvel Rivals Discord Bot

This is a Discord bot written in Python using the discord.py library that generates humorous roasts based on a player's in-game stats. It uses the OpenAI API to generate text based on a prompt.

## Technologies Used

- Python 3.12
- discord.py
- OpenAI API
- Docker
- Github Actions CI/CD: Automatically deploy to AWS EC2

## Configuration

Create a `.env` file with the following variables:

- `DISCORD_TOKEN`: Your bot's Discord token
- `OPENAI_API_KEY`: Your OpenAI API key
- `API_BASE_URL`: The base URL of the API that provides player data

## Running the bot

Run `docker-compose up --build` to start the bot

## Commands

- `!roast <marvel_rivals_username>`: Generates a roast for the given player based on their in-game stats.

## Roadmap

- Add more commands for different types of roasts (e.g. roasting a player's favorite hero)
- Add more features for customizing the roasts (e.g. adding a custom image or font)
- Add support for other games (e.g. Overwatch, Apex Legends)
