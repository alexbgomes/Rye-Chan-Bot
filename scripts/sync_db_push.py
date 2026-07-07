import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

PI_USER = os.getenv("PI_USER")
PI_HOST = os.getenv("PI_HOST")
PI_PATH = os.getenv("PI_PATH")
DB_PATH = "data/bot_database.sqlite3"

if not all([PI_USER, PI_HOST, PI_PATH]):
    print("Error: PI_USER, PI_HOST, or PI_PATH is missing from your .env file.")
    print("Please check your .env file and ensure they are set.")
    exit(1)

if not os.path.exists(DB_PATH):
    print(f"Error: Could not find local database at {DB_PATH}")
    print("Please make sure you are running this script from the root of the Rye-Chan-Bot project.")
    exit(1)

print(f"Preparing to PUSH {DB_PATH} to {PI_USER}@{PI_HOST}:{PI_PATH}...")
print("Executing SCP command...")

# scp data/bot_database.sqlite3 pi@192.168.1.xxx:/home/pi/Rye-Chan-Bot/data/bot_database.sqlite3
command = ["scp", DB_PATH, f"{PI_USER}@{PI_HOST}:{PI_PATH}"]

try:
    subprocess.run(command, check=True)
    print("Success! Database push complete.")
except subprocess.CalledProcessError as e:
    print(f"\nPush failed. Error code: {e.returncode}")
    print("Double check that your PI_HOST IP address is correct and the PI_PATH exists on the Pi.")
except FileNotFoundError:
    print("\nError: The 'scp' command is not installed or not in your PATH.")
    print("Windows 10/11 usually has OpenSSH installed by default. You may need to enable it in Windows Settings.")
