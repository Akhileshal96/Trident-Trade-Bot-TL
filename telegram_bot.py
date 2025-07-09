from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from state_manager import is_bot_running, stop_bot, resume_bot
from performance_logger import get_last_log_summary

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USERS = list(map(int, os.getenv("AUTHORIZED_USERS").split(",")))

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS


@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    if not is_authorized(event.sender_id):
        return
    await event.respond("🤖 *Trident Bot Ready!*\nUse these commands:\n\n"
                        "/status - Show current status\n"
                        "/log - Show last trades\n"
                        "/stop - Pause bot\n"
                        "/resume - Resume bot\n"
                        "/token <token> - Update Zerodha token\n"
                        "/setprofit <amount>\n"
                        "/setloss <amount>\n"
                        "/setcapital <amount>", parse_mode='markdown')


@client.on(events.NewMessage(pattern="/status"))
async def status_handler(event):
    if not is_authorized(event.sender_id):
        return
    status = "🟢 Running" if is_bot_running() else "🔴 Paused"
    await event.respond(f"Bot Status: {status}")


@client.on(events.NewMessage(pattern="/stop"))
async def stop_handler(event):
    if not is_authorized(event.sender_id):
        return
    stop_bot()
    await event.respond("🛑 Trading paused.")


@client.on(events.NewMessage(pattern="/resume"))
async def resume_handler(event):
    if not is_authorized(event.sender_id):
        return
    resume_bot()
    await event.respond("✅ Trading resumed.")


@client.on(events.NewMessage(pattern="/log"))
async def log_handler(event):
    if not is_authorized(event.sender_id):
        return
    summary = get_last_log_summary()
    await event.respond(f"📊 *Last Trades:*\n{summary}", parse_mode='markdown')


@client.on(events.NewMessage(pattern=r"/token (.+)"))
async def token_handler(event):
    if not is_authorized(event.sender_id):
        return
    token = event.pattern_match.group(1)
    with open(".env", "r") as file:
        lines = file.readlines()
    with open(".env", "w") as file:
        for line in lines:
            if line.startswith("ZERODHA_ACCESS_TOKEN="):
                file.write(f"ZERODHA_ACCESS_TOKEN={token}\n")
            else:
                file.write(line)
    await event.respond("🔑 Access token updated. Restart the bot to apply.")


@client.on(events.NewMessage(pattern=r"/setprofit (\d+)"))
async def set_profit_handler(event):
    if not is_authorized(event.sender_id):
        return
    amount = event.pattern_match.group(1)
    os.environ["MAX_PROFIT"] = amount
    await event.respond(f"💰 Max profit set to ₹{amount}")


@client.on(events.NewMessage(pattern=r"/setloss (\d+)"))
async def set_loss_handler(event):
    if not is_authorized(event.sender_id):
        return
    amount = event.pattern_match.group(1)
    os.environ["MAX_LOSS"] = amount
    await event.respond(f"⚠️ Max loss set to ₹{amount}")


@client.on(events.NewMessage(pattern=r"/setcapital (\d+)"))
async def set_capital_handler(event):
    if not is_authorized(event.sender_id):
        return
    amount = event.pattern_match.group(1)
    os.environ["WALLET_CAPITAL"] = amount
    await event.respond(f"🏦 Wallet capital set to ₹{amount}")


def start_telegram_bot():
    print("✅ Telegram bot started.")
    client.run_until_disconnected()
