
# 📘 Project Documentation: TPC BOT

---

![TPC BOT Banner](https://cdn.discordapp.com/avatars/1196199588558819449/a_3a562b89e7a14205baf010e3eaf18c1a.gif?size=1024)

---

## 🔥 Overview

**TPC BOT** is a powerful, multifunctional Discord bot designed to enhance comfort and fun on your server. With over 5000 lines of code, it includes a wide range of commands — from entertainment and utility features to complex moderation tools.

The bot is actively used in communities and has positive feedback. You can check out its page on [top.gg](https://top.gg/bot/1196199588558819449) for more info, ratings, and reviews.

---

![TPC BOT Additional](https://i.imgur.com/9JavKJc.jpeg)

---

## 🛠 Technologies and Architecture

- **Language:** Python 3.x
- **Library:** `disnake` (an asynchronous Discord API library)
- **Architecture:** Modular, split into commands, moderation features, AI generators, and more
- **Size:** Over 5000 lines of code ensuring flexibility and scalability

---

## 🚀 Main Features

### 🎉 Entertainment and Utility Commands

- `/video` — play videos on demand
- `/random_video` — random videos for a good mood
- `/google` — quick Google search
- `/github_find` — search GitHub repositories
- `/translate` — instant text translation between languages
- `/twitter` — search tweets by keywords
- `/flipcoin` — coin flip for decision making
- `/dadjoke` and `/teacherjoke` — witty jokes to lighten the mood
- `/clubfinder` — find interesting clubs or communities
- `/happy` — sends positive quotes and vibes
- `/findmovie` — movie information search
- `/artgen` — AI-powered image generation

### 🛡 Moderation Commands

- Voice channels: `/deafen`, `/undeafen`, `/massmove` — control user states
- Messaging: `/send`, `/say`, `/call`, `/notifyall` — mass and targeted notifications
- Admin commands: `/warn`, `/kick`, `/ban`, `/mute`, `/unmute`, `/unban` — control user behavior
- Ranks and roles: `/addrank`, `/delrank`, `/ranks`, `/roleinfo`, `/temprole` — flexible rights management
- Other: `/clear` — clear chats, `/autosending` — automated message sending
- **RoleMenuCog** — interactive menu for users to self-assign roles

### ℹ️ System Commands

- `/help` — interactive help with buttons linking to the official commands list and support server
- `/invite` — quick access to invite link to add the bot to your server
- `/info` — general info about the bot, its capabilities, and philosophy

---

## 📂 Project Structure

```
TPC_BOT/
│
├── main.py                # Entry point, bot setup and launch
├── TPC/
│   └── commands/
│       └── core/
│           └── main.py    # Main entertainment and utility commands
├── commands/
│   └── moderation.py      # Moderation commands
│   └── main/
│       └── vs.py          # (planned voice commands)
├── cogs/
│   └── rolemenu.py        # Role menu extension
└── utils/
    └── helpers.py         # Bot utilities
```

---

## ⚙️ Setup and Run

1. Install dependencies:

```bash
pip install disnake
```

```bush
pip install -r requirements.txt
```


2. Set the `TOKEN` variable in `main.py` with your Discord bot token.

3. Run the bot:

```bash
python main.py
```

---

## 🔗 Useful Links

- Official bot page on top.gg:  
  [https://top.gg/bot/1196199588558819449](https://top.gg/bot/1196199588558819449)

- Commands page:  
  [https://iliapiasta.github.io/TcP/pages/commands.html](https://iliapiasta.github.io/TcP/pages/commands.html)

- Support server:  
  [Discord Support Server](https://discord.com/channels/1242558139262435328/1275577431658594356)

---

## 🙌 Contact Information

If you have questions, ideas, or want to contribute — join the support server or contact me directly.

---

If you need, I can help create a README.md or detailed documentation with usage examples!
