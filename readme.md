# Rye-Chan-Bot V3.0

Rye-Chan-Bot has been rewritten from C# to Python, utilizing the modern `discord.py` API wrapper. This ensures better maintainability, performance on the Raspberry Pi 3B+, and access to modern Discord features like Slash Commands.

## Setup Instructions

1. **Install Python 3.10+** (Required for modern `discord.py`).
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the bot:
   - Create a `.env` file containing your `DISCORD_TOKEN=your_token_here`.
   - Update `config.yaml` as necessary (e.g. SQLite database path).
5. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

### Fun Commands
- `/xkcd`: Get a random xkcd comic.
- `/8ball`: Ask the magic 8ball a question.
- `/mock`: MoCkS TeXt LiKe ThIs.
- `/confess`: Submit an anonymous confession instantly.
- `/morph`: Morphs a word down line by line.
- `/feels`: Posts a random pepe image.
- `/pick`: Picks a random choice from a comma-separated list.
- `/fact`: Posts a random fun fact.
- `/say`: Makes the bot echo your message.
- `/inspiro`: Posts a randomly generated quote from inspirobot.me.
- `/dadjoke`: Posts a random dad joke.
- `/urban`: Searches Urban Dictionary for a term.

### Utility Commands
- `/ping`: Replies with the bot's latency (Pong!).
- `/about`: About Rye-Chan-Bot.
- `/help`: Shows a list of available commands.
- `/desc`: Posts the topic of the current channel.
- `/avatar`: Returns the link to a user's avatar.
- `/conv`: Convert a number between bases (dec, hex, oct, bin).
- `/page`: Moves the chat up to clear messages visually (Bulk deletes 40 messages).
- `/playing`: Returns a list of users playing the inquired game.
- `/members`: Returns a list of people in the inquired role.
- `/trim`: Bulk deletes a specified number of messages.
- `/whois`: Returns detailed user data.
- `/tex`: Returns LaTeX formatted image.
- `/translate`: Translates text from source language to destination language.
- `/translate_langs`: Returns a list of supported languages for translation.
- `/quote`: Quotes a message in the same channel using its ID.
