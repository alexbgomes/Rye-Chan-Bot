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
