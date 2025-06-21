from flask import Flask
import threading
import asyncio
import time
import aiohttp
import random
import string
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Your constants and async functions here
ALLOWED_EXTENSIONS = [
    ".mp4", ".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp3", ".pdf", ".txt",
    ".zip", ".rar", ".7z", ".wav", ".bmp", ".svg"
]

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"]
VIDEO_EXTENSIONS = [".mp4", ".webm"]

MAX_RETRIES = 3
CONCURRENCY = 20
OUTPUT_FILE = "links.txt"
TOTAL_ATTEMPTS = 0  # 0 = infinite
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1251634016730353704/UgnEZghf-ftHv7H95WDNvZeafw_SZZQvAlMpdr5GTOQVj7wdeu0p6YMHNfJK3AczkRoe" # REPLACE THIS WITH YOUR DISCORD WEBHOOK


def print_banner():
    banner = r"""
  ______               __      __                                                                 
 /      \             /  |    /  |                                                                
/$$$$$$  |  ______   _$$ |_   $$ |____    ______   __    __      _____  ____    ______    ______  
$$ |  $$/  /      \ / $$   |  $$      \  /      \ /  \  /  |    /     \/    \  /      \  /      \ 
$$ |       $$$$$$  |$$$$$$/   $$$$$$$  |/$$$$$$  |$$  \/$$/     $$$$$$ $$$$  |/$$$$$$  |/$$$$$$  |
$$ |   __  /    $$ |  $$ | __ $$ |  $$ |$$ |  $$ | $$  $$<      $$ | $$ | $$ |$$ |  $$ |$$    $$ |
$$ \__/  |/$$$$$$$ |  $$ |/  |$$ |__$$ |$$ \__$$ | /$$$$  \  __ $$ | $$ | $$ |$$ \__$$ |$$$$$$$$/ 
$$    $$/ $$    $$ |  $$  $$/ $$    $$/ $$    $$/ /$$/ $$  |/  |$$ | $$ | $$ |$$    $$/ $$       |
 $$$$$$/   $$$$$$$/    $$$$/  $$$$$$$/   $$$$$$/  $$/   $$/ $$/ $$/  $$/  $$/  $$$$$$/   $$$$$$$/ 
                                                                                                  
                                                                                                                                                                                                  
        Catbox Link Checker - made by https://github.com/BlitZzZ124
    """
    print(Fore.CYAN + banner)


def generate_random_filename():
    name = ''.join(random.choices(string.ascii_lowercase, k=6))
    ext = random.choice(ALLOWED_EXTENSIONS)
    return name + ext


async def send_webhook(session, url):
    if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_HERE":
        return

    ext = url[-4:].lower()
    embed = {
        "title": "✅ Catbox Link Found",
        "description": f"[Click to view]({url})",
        "color": 0x00ff00,
        "author": {
            "name": "Made by BlitZ",
            "url": "https://github.com/BlitZzZ124",
            "icon_url": "https://i.imgur.com/IkhAcl8.jpeg"
        }
    }

    if ext in IMAGE_EXTENSIONS:
        embed["image"] = {"url": url}
    elif ext in VIDEO_EXTENSIONS:
        embed["video"] = {"url": url}

    payload = {"embeds": [embed]}

    try:
        async with session.post(WEBHOOK_URL, json=payload) as resp:
            if resp.status not in [200, 204]:
                print(f"{Fore.RED}[WEBHOOK ERROR] Status: {resp.status}")
    except Exception as e:
        print(f"{Fore.RED}[WEBHOOK ERROR] → {e}")



async def check_link(session, sem, url):
    async with sem:
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept":
            "*/*",
        }

        for attempt in range(1, MAX_RETRIES + 1):
            print(
                f"{Fore.YELLOW}[CHECKING]{Style.RESET_ALL} {url} (Attempt {attempt})"
            )
            try:
                async with session.get(url,
                                       headers=headers,
                                       timeout=10,
                                       allow_redirects=False) as resp:
                    if resp.status == 200:
                        print(f"{Fore.GREEN}[VALID]   {url}")
                        with open(OUTPUT_FILE, "a") as f:
                            f.write(url + "\n")
                        await send_webhook(session, url)
                        return
                    else:
                        print(
                            f"{Fore.RED}[INVALID] {url} (status: {resp.status})"
                        )
                        return
            except Exception as e:
                print(f"{Fore.RED}[ERROR]   {url} → {e}")
                await asyncio.sleep(0.5 * attempt)


async def main():
    print_banner()
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        # 🔔 Notify on startup
        if WEBHOOK_URL:
            try:
                await session.post(WEBHOOK_URL, json={"content": "🚀 Catbox Checker is now running!"})
            except Exception as e:
                print(f"{Fore.RED}[WEBHOOK ERROR] Failed to notify startup → {e}")

        attempt = 0
        while True:
            if TOTAL_ATTEMPTS and attempt >= TOTAL_ATTEMPTS:
                break
            attempt += 1
            filename = generate_random_filename()
            url = f"https://files.catbox.moe/{filename}"
            asyncio.create_task(check_link(session, sem, url))
            await asyncio.sleep(0.05)



# Flask app setup
app = Flask(__name__)


@app.route('/')
def home():
    return "I'm alive!"


def start_async_loop():
    asyncio.run(main())


if __name__ == "__main__":
    # Start async task checker in a separate daemon thread
    threading.Thread(target=start_async_loop, daemon=True).start()

    # Start Flask web server on main thread
    app.run(host='0.0.0.0', port=3000)
