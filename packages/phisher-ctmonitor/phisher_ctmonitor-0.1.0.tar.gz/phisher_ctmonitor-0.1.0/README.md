# Phisher

[![PyPI version](https://img.shields.io/pypi/v/phisher)](https://pypi.org/project/phisher/) [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![Python](https://img.shields.io/badge/python-3.7%2B-green)](https://www.python.org/)

> A rich‐powered CLI tool for monitoring Certificate Transparency (CT) logs and alerting on domains matching your keywords.

---

## 📖 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Examples](#-examples)
- [Configuration](#-configuration)
- [Notifications](#-notifications)
- [Logging & Output](#-logging--output)

---

## 🔥 Features

- **Real-time monitoring** of CT logs for newly issued certificates  
- **Keyword matching**: scan domains against CLI‐provided or file‐based keyword lists  
- **Rich CLI** using [rich](https://github.com/Textualize/rich) & [rich‐argparse](https://github.com/jonparrott/rich-argparse) for beautiful output  
- **Notifications** via Telegram bot (chat ID + bot token)  
- **Flexible output**: append matches to `.txt` or `.csv`  
- **Colorful ASCII banner** with gradient styling  

---

## 🚀 Installation

```bash
pip install phisher
```

Or clone and install from source:

```
git clone https://github.com/yourusername/phisher.git
cd phisher
pip install .
```

## 💻 Usage

```
Flag	Arguments	Description
-n, --notify	CHAT_ID BOT_TOKEN	Enable Telegram notifications (provide your chat ID and bot token).
-l, --log	—	Enable logging to file (defaults to domains.txt).
-k, --keywords	KEY1 KEY2 …	Space-separated list of keywords to match against domain names.
-kf, --keywords-file	path/to/file.txt	Path to a newline-separated file of keywords (default: keywords.txt).
-f, --format	csv | txt	Output format for matches: CSV or TXT (default: txt).
-o, --output-file	path/to/output.txt	File to append matching domain reports (default: domains.txt).
-h, --help	—	Show help message and exit.
```

## 🎯 Examples

Start Monitoring

```
phisher
```

Monitor with a keyword file

```
phisher --keywords-file my_keywords.txt --format csv --output-file alerts.csv
```

Monitor with Telegram notifications, --notify expects chat_id and telegram_bot_token

```
phisher -kf keywords.txt -n -1234567890123 123456789:ABCDEFghiJklMNopQRStuvWXyz
```

Enable file logging and provide inline keywords

    phisher --log --keywords dhl reddit microsoft

## ⚙️ Configuration

If you have a long list of arguments, you can store them in a file called keywords.txt, with one keyword per line:

```
reddit
microsoft
dhl
office365
```
Alternatively, save the keywords in any other file and provide its path using the --output-file (-o) parameter.

Parameters needed to avoid rate limiting are defined in config.py. Feel free to adjust them if you find them too strict.

## 🔔 Notifications

To receive instant alerts via Telegram:

Create a Bot via BotFather and get your BOT_TOKEN.

Find your CHAT_ID (e.g., by messaging your bot and querying @userinfobot).

You can use this article to help you with this matter: https://andrewkushnerov.medium.com/how-to-send-notifications-to-telegram-with-python-9ea9b8657bfb

Run:

    phisher --notify <CHAT_ID> <BOT_TOKEN> ...

## 📝 Logging & Output

    TXT format (default):
    Appends certificate details to domains.txt.

    CSV format:
    Outputs rows with columns like "Subject", "Issuer", "Serial No", "Version", "Not Before (UTC)", "Not After (UTC)".

Enable logging file creation with --log (otherwise, logging is disabled and only prints to console).