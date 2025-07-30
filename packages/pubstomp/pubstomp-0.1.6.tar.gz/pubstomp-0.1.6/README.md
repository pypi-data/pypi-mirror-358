# PubStomp

**PubStomp** is an asynchronous pentesting toolkit designed for efficient reconnaissance, vulnerability fuzzing, and reporting against web applications.

- 📦 PyPI: [https://pypi.org/project/pubstomp](https://pypi.org/project/pubstomp)
- 🐙 GitHub: [https://github.com/nolancoe/PubStomp](https://github.com/nolancoe/PubStomp)

## Features
- 🔎 Async web crawling and spidering
- 🎯 Custom wordlists for fuzzing endpoints
- 🔐 Optional XSS payload testing with configurable wordlists
- 🧪 Report generation to JSON
- 🎨 Colored terminal output with progress bars
- 💾 Configurable output, log file, XSS payloads, and Nmap arguments
- 🧰 Optional Burp Suite integration for proxying requests

## Installation
Install from PyPI:

```bash
pip install pubstomp
```

> ⚠️ On some systems (like Kali Linux), system Python may be restricted.
>
> To safely install PubStomp:
>
> **Option 1** – Use `pipx`:
>
> ```bash
> pipx install pubstomp
> ```
>
> **Option 2** – Use a virtual environment:
>
> ```bash
> python3 -m venv env
> source env/bin/activate
> pip install pubstomp
> ```
>
> **Option 3** – Allow pip to install locally:
>
> ```bash
> pip install --user pubstomp
> export PATH="$HOME/.local/bin:$PATH"
> ```

## Usage Examples

Set your output, log, XSS wordlist, and Nmap scan args:

```bash
pubstomp --setoutput ~/targets
pubstomp --setlog ~/logs/pubstomp.log
pubstomp --setxss ~/wordlists/xss.txt
pubstomp --setnmap "-sS -T4"
```

Check configured paths:

```bash
pubstomp --showoutput
pubstomp --showlog
pubstomp --showxss
pubstomp --shownmap
```

Reset configurations:

```bash
pubstomp --resetxss
pubstomp --resetnmap
```

Example scans:

```bash
# Crawl with depth 2, enable XSS fuzzing, generate a report, delay 0, workers 15
pubstomp example.com --depth 2 --xss --report --delay 0 --workers 15

# Fuzz using a custom wordlist, skip crawling
pubstomp example.com --nocrawl --wordlist path/to/wordlist.txt --report

# Proxy requests through Burp Suite (default: http://127.0.0.1:8080)
pubstomp example.com --burp

# Default scan with Nmap integration and report
pubstomp example.com --report
```

## Command-Line Arguments

| Flag | Description |
|------|-------------|
| `--depth` | Max crawl depth (default: 2) |
| `--xss` | Enable XSS payload fuzzing |
| `--report` | Generate a JSON report file |
| `--nonmap` | Skip Nmap integration |
| `--nocrawl` | Disable automatic crawling |
| `--burp` | Route all HTTP(S) requests through a Burp Suite proxy |
| `--wordlist` | Path to wordlist for manual fuzzing |
| `--cookies` | Custom cookie string to include in requests |
| `--delay` | Delay (in seconds) between requests |
| `--workers` | Number of concurrent async workers |
| `--setoutput` | Persistently set output directory |
| `--setlog` | Persistently set log file path |
| `--setxss` | Set custom wordlist path for XSS testing |
| `--showoutput` | Display current output directory |
| `--showlog` | Display current log file path |
| `--showxss` | Display current XSS wordlist path |
| `--resetxss` | Clear saved XSS path and return to default payloads |
| `--setnmap` | Set custom Nmap arguments (e.g. `-sS -T4`) |
| `--shownmap` | Show current Nmap arguments |
| `--resetnmap` | Reset Nmap arguments to default: `--script vuln -A` |

## Configuration File

Your configuration is stored in:
```
~/.config/pubstomp/config.json
```

This includes paths for:
- Target output directory
- Log file
- XSS payload wordlist
- Custom Nmap argument string

## License
This project is licensed under the MIT License.
