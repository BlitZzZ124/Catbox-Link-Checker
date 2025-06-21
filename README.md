# 🐱 Catbox Link Checker

A fast, asynchronous tool that generates and checks random [Catbox.moe](https://catbox.moe) file links to find valid files — including support for Discord webhooks with media previews!

---

## ✨ Features

- 🔄 **Generates random Catbox URLs**
- ⚡ **Ultra-fast async checking** (via `aiohttp`)
- ✅ **Saves valid links to `links.txt`**
- 🎯 **Sends valid results to a Discord webhook with embeds**
- 🖼️ **Auto-displays images and videos in embed previews**
- 🔒 **Uses environment variable for webhook**
- 🔁 **Run forever or limit by attempt count**

---

## 📦 Requirements

Install the dependencies:

```bash
pip install -r requirements.txt
