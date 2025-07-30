# Phisher

[![PyPI version](https://img.shields.io/pypi/v/phisher)](https://pypi.org/project/phisher/) [![Python](https://img.shields.io/badge/python-3.7%2B-green)](https://www.python.org/)

> Phisher is a real-time tool designed to monitor Certificate Transparency logs. By default, it displays all newly discovered domains directly in your console. You can also filter the results using specific keywords, set up instant Telegram notifications whenever there's a match, and save certificate details to a file in plain text or CSV format. If you don’t specify keywords or provide a keyword file, Phisher will simply show every domain it finds.

---

## 📖 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Keyword Filtering](#keyword-filtering)
- [Notifications](#notifications)
- [Logging & Output](#logging--output)
---

## 🔥 Features

- ✅ Real-time monitoring of Certificate Transparency logs
- 🔎 Domain filtering using keywords or wildcard patterns
- 📬 Telegram notifications for matched domains
- 📄 Log certificate details in `.txt` or `.csv` format
- 🎨 Stylish CLI interface powered by [`rich`](https://github.com/Textualize/rich)


---

## 🚀 Installation

```bash
pip install phisher-ctmonitor
```

Or clone and install from source:

```
git clone https://github.com/yourusername/phisher.git
cd phisher
pip install .
```

## 💻 Usage

```
Usage: Phisher [-h] [--keywords KEYWORDS [KEYWORDS ...]] [--keywords-file KEYWORDS_FILE] [--notify CHAT_ID BOT_TOKEN] [--log]
               [--format {csv,txt}] [--output-file OUTPUT_FILE]

Options:
  -h, --help            show this help message and exit
  --keywords, -k KEYWORDS [KEYWORDS ...]
                        Provide inline keywords (space-separated) to filter matching domains. Supports wildcards using '*', e.g.,
                        'dhl*com'.
  --keywords-file, -kf KEYWORDS_FILE
                        Path to a newline-separated file of keywords. Wildcards supported.
  --notify, -n CHAT_ID BOT_TOKEN
                        Enable Telegram notifications. Requires your Telegram chat ID and bot token.
  --log, -l             Enable logging of certificate data. Defaults to 'domains.txt'.
  --format, -f {csv,txt}
                        Choose output format: plain text or CSV. Default is 'txt'.
  --output-file, -o OUTPUT_FILE
                        Custom path to the log file. If omitted, defaults to 'domains.txt'.
```

## 🎯 Examples

Run in default mode (prints all domains):

```
phisher
```

Filter using a keyword file and output to CSV:

```
phisher --keywords-file my_keywords.txt --format csv --output-file alerts.csv
```

Enable Telegram notifications, use the keywords from the keyowrds.txt file

```
cat keywords.txt
dhl*sk
alza*cz
microsoft
office*365


phisher -n -123456789 123456789:ABCDEFghiJklMNopQRStuvWXyz
```

Inline keyword filtering with logging in plain text format to domains.txt file:
```
phisher --log --keywords dhl reddit microsoft alza*cz
```

## 🔤 Keyword Filtering

Phisher supports keyword-based domain filtering, allowing you to use wildcards (*) within keywords. By default, Phisher reads keywords from a file named keywords.txt, located in your current directory. If you prefer to use a different keyword file, you can specify its path using the --keywords-file argument. Additionally, you can provide keywords directly through the command line using the --keywords argument, separating each keyword with spaces. If both inline keywords and a keyword file are specified, Phisher will combine and use keywords from both sources. 

f there is no keywords.txt file, the provided keywords file is empty, and no keywords are specified via command-line arguments, Phisher **will display all domains it encounters**.

### ✅ Inline Example:

Phisher will return domains containing either dhl\*com or paypal\*.

```
phisher --keywords dhl*com paypal*
```

### ✅ File Example:

Phisher will return domains containing either paypal or matching the wildcard pattern alza*cz.

```
cat myfile.txt
paypal
alza*cz


phisher --keywords-file myfile.txt
```

### ✅ Combined Example:

Phisher will return domains containing either paypal or matching the wildcard pattern alza*cz.

```
cat keywords.txt
paypal


phisher --keywords alza*cz
```

If no keywords are specified, Phisher will show all discovered domains.

## 🔔 Notifications

You can receive real-time alerts for matched domains via Telegram.

How to set up:

1. Create a bot using BotFather and get your BOT_TOKEN.

2. Find your CHAT_ID by messaging your bot and using @userinfobot.

3. Run:
```
phisher --notify <CHAT_ID> <BOT_TOKEN> ...
```

For more information reffer to the article: https://andrewkushnerov.medium.com/how-to-send-notifications-to-telegram-with-python-9ea9b8657bfb

When a match is found, you’ll receive a message like:

```
Found domain: login-paypal-alerts.com
```

## 📝 Logging & Output

Data is always appended, not overwritten.

You can use --output-file to specify a custom path.

### 🔹 TXT Format (Default)

Plaintext output appended to domains.txt (or your specified output file).

```
[*] Found domain: example.com
Subject:     CN=example.com
Issuer:      CN=R11,O=Let's Encrypt,C=US
Serial No.:  491941814344993082078629210346161435118923
Version:     v3
Validity:
  Not Before (UTC): 2025-06-30 06:08:29+00:00
  Not After  (UTC): 2025-09-28 06:08:28+00:00
```
### 🔹 CSV Format

```
CN=example.com,"CN=Go Daddy Secure Certificate Authority - G2,OU=http://certs.godaddy.com/repository/,O=GoDaddy.com\, Inc.,L=Scottsdale,ST=Arizona,C=US",9646021474962679931,v3,2024-07-12 15:54:09+00:00,2025-07-12 15:54:09+00:00
```