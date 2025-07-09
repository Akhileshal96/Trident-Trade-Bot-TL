import os
from dotenv import load_dotenv

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY")
ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

def update_token_in_env(new_token):
    """
    Replaces the ZERODHA_ACCESS_TOKEN in the .env file
    """
    updated = False
    with open(".env", "r") as f:
        lines = f.readlines()

    with open(".env", "w") as f:
        for line in lines:
            if line.startswith("ZERODHA_ACCESS_TOKEN="):
                f.write(f"ZERODHA_ACCESS_TOKEN={new_token}\n")
                updated = True
            else:
                f.write(line)

    if not updated:
        with open(".env", "a") as f:
            f.write(f"ZERODHA_ACCESS_TOKEN={new_token}\n")
