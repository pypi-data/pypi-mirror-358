#!/usr/bin/env python3
import argparse
import cmd
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlencode
import time
import os
import sys
import subprocess
import re
import logging
from logging.handlers import RotatingFileHandler
import json
from colorama import init, Fore, Style
from tqdm import tqdm
import validators


CONFIG_PATH = os.path.expanduser("~/.config/pubstomp/config.json")

def load_config_key(key):
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
                return data.get(key)
        except Exception:
            pass
    return None


def save_config_key(key, value):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    config = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
        except Exception:
            pass
    config[key] = value
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)


def load_xss_payloads():
    custom_path = load_config_key("xss_path")
    if custom_path and os.path.isfile(custom_path):
        try:
            with open(custom_path, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"⚠️ Failed to read custom XSS wordlist: {e}. Falling back to defaults.")
    
    return [
        "<script>alert(1)</script>",
        "\"><img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        "'><script>alert(1)</script>"
    ]


class SimpleSpider:
    def __init__(self, base_url, max_depth=1, delay=0.1, wordlist=None, workers=10, cookies=None, no_verify_ssl=False):
        self.base_url = base_url.rstrip('/')
        self.parsed_base = urlparse(self.base_url)
        self.max_depth = max_depth
        self.delay = delay
        self.visited = set()
        self.wordlist = wordlist or []
        self.workers = workers
        self.cookies = cookies or {}
        self.no_verify_ssl = no_verify_ssl
        self.logger = logging.getLogger(__name__)
        self.static_assets = []
        self.forms = []
        self.xss_results = []
        self.rate_limited = False
        self.semaphore = asyncio.Semaphore(workers)

        self.XSS_PAYLOADS = load_xss_payloads()


    


    def same_domain(self, url):
        return urlparse(url).netloc == self.parsed_base.netloc

    def normalize(self, link, current_url):
        abs_link = urljoin(current_url, link.split('#')[0])
        return abs_link.rstrip('/')

    async def fetch_links(self, session, url):
        async with self.semaphore:
            try:
                async with session.get(url, timeout=10, allow_redirects=True, ssl=not self.no_verify_ssl) as resp:
                    if resp.status >= 400:
                        self.logger.error(f"Failed to fetch {url}: HTTP {resp.status}")
                        if resp.status == 429:
                            self.rate_limited = True
                        return []
                    content = await resp.read()
                    ctype = resp.headers.get('Content-Type', '').lower()
                    self.logger.info(f"Fetched {url} (Status: {resp.status}, Size: {len(content)} bytes, Content-Type: {ctype})")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                self.logger.error(f"Failed to fetch {url}: {e}")
                if isinstance(e, aiohttp.ClientResponseError) and e.status == 429:
                    self.rate_limited = True
                return []

            if 'text/html' not in ctype and 'text' not in ctype:
                if any(url.split('?')[0].lower().endswith(ext) for ext in ('.mp3', '.pdf', '.zip', '.jpg', '.png', '.mp4', '.css', '.txt', '.gz')):
                    self.static_assets.append((url, ctype or 'unknown'))
                    self.logger.info(f"Found static asset: {url} (MIME: {ctype or 'unknown'})")
                return []

            try:
                soup = BeautifulSoup(content, 'html.parser')
                links = [self.normalize(a['href'], url) for a in soup.find_all('a', href=True)]
                forms = soup.find_all('form')
                if forms:
                    self.logger.info(f"Found {len(forms)} forms on {url}")
                    for form in forms:
                        form_details = {
                            'url': url,
                            'action': self.normalize(form.get('action', ''), url) if form.get('action') else url,
                            'method': form.get('method', 'GET').upper(),
                            'inputs': []
                        }
                        for input_tag in form.find_all('input'):
                            input_details = {
                                'name': input_tag.get('name', ''),
                                'type': input_tag.get('type', ''),
                                'id': input_tag.get('id', '')
                            }
                            form_details['inputs'].append(input_details)
                        self.forms.append(form_details)
                self.logger.debug(f"Extracted {len(links)} links from {url}")
                return links
            except Exception as e:
                self.logger.error(f"Failed to parse HTML for {url}: {e}")
                return []

    async def test_xss_form(self, session, form, xss_pbar):
        """Test a form for XSS by submitting payloads and checking for reflection."""
        action = form['action']
        method = form['method']
        inputs = form['inputs']
        results = []
        for payload in self.XSS_PAYLOADS:
            data = {input_field['name']: payload for input_field in inputs if input_field['name']}
            if not data:
                xss_pbar.update(1)
                continue
            try:
                if method.upper() == 'POST':
                    async with session.post(action, data=data, timeout=5, ssl=not self.no_verify_ssl) as resp:
                        content = await resp.text()
                        status = "Reflected" if payload in content else "Not Reflected"
                        results.append({
                            'url': action,
                            'payload': payload,
                            'status': status,
                            'response_status': resp.status
                        })
                        if status == "Reflected":
                            self.logger.info(f"XSS candidate: {payload} reflected in {action} (Status: {resp.status})")
                        else:
                            self.logger.debug(f"XSS test: {payload} not reflected in {action} (Status: {resp.status})")
                else:
                    params = urlencode(data)
                    test_url = f"{action}?{params}" if '?' not in action else f"{action}&{params}"
                    async with session.get(test_url, timeout=5, ssl=not self.no_verify_ssl) as resp:
                        content = await resp.text()
                        status = "Reflected" if payload in content else "Not Reflected"
                        results.append({
                            'url': test_url,
                            'payload': payload,
                            'status': status,
                            'response_status': resp.status
                        })
                        if status == "Reflected":
                            self.logger.info(f"XSS candidate: {payload} reflected in {test_url} (Status: {resp.status})")
                        else:
                            self.logger.debug(f"XSS test: {payload} not reflected in {test_url} (Status: {resp.status})")
            except aiohttp.ClientError as e:
                results.append({
                    'url': action,
                    'payload': payload,
                    'status': f"Error: {e}",
                    'response_status': None
                })
                self.logger.error(f"XSS test failed for {action}: {e}")
            xss_pbar.update(1)
            await asyncio.sleep(self.delay)
        return results

    async def fuzz_url(self, session, word):
        candidate = f"{self.base_url}/{word}"
        async with self.semaphore:
            try:
                async with session.head(candidate, timeout=3, allow_redirects=True, ssl=not self.no_verify_ssl) as r:
                    if r.status < 400:
                        self.logger.info(f"Fuzz hit: {candidate} (Status: {r.status})")
                        return candidate
                    elif r.status == 429:
                        self.rate_limited = True
            except (aiohttp.ClientError, asyncio.TimeoutError):
                pass
            return None

    async def brute_force(self, session):
        found = []
        self.logger.info(f"Starting fuzzing with {len(self.wordlist)} words")
        tasks = [self.fuzz_url(session, word) for word in self.wordlist]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fuzzing"):
            result = await f
            if result:
                found.append(result)
            if self.rate_limited:
                self.logger.warning("Rate limit detected (HTTP 429). Increasing delay.")
                self.delay *= 2
                self.rate_limited = False
            await asyncio.sleep(self.delay)
        return found

    async def fetch_robots(self, session):
        robots_url = f"{self.base_url}/robots.txt"
        try:
            async with session.get(robots_url, timeout=5, ssl=not self.no_verify_ssl) as resp:
                if resp.status >= 400:
                    return []
                text = await resp.text()
                disallowed = [
                    line.split(':', 1)[1].strip()
                    for line in text.splitlines()
                    if line.lower().startswith('disallow:')
                ]
                self.logger.info(f"Found {len(disallowed)} disallowed paths in robots.txt")
                return [path.lstrip('/') for path in disallowed if path.lstrip('/')]
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return []

    async def crawl(self, session):
        from tqdm import tqdm
        print(f"{Fore.GREEN}▶️ Starting Crawl…{Style.RESET_ALL}")
        pbar = tqdm(desc="Crawling pages", unit="url")
        crawl_count = 0
        queue = [(self.base_url, 0)]
        discovered = []
        redirect_count = {}

        while queue:
            batch = []
            while queue and len(batch) < self.workers:
                batch.append(queue.pop(0))
            tasks = []
            batch_urls = []
            for url, depth in batch:
                if url in self.visited or depth > self.max_depth:
                    continue
                batch_urls.append((url, depth))
                tasks.append(self.fetch_links(session, url))

            if not tasks:
                continue

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for (url, depth), children in zip(batch_urls, results):
                if isinstance(children, Exception):
                    self.logger.error(f"Error crawling {url}: {children}")
                    continue
                self.visited.add(url)
                crawl_count += 1
                pbar.update(1)
                discovered.append(url)
                self.logger.debug(f"Processing {url} at depth {depth}, found {len(children)} links")
                for link in children:
                    if self.same_domain(link) and link not in self.visited:
                        redirect_count[link] = redirect_count.get(link, 0) + 1
                        if redirect_count[link] > 3:
                            self.logger.warning(f"Skipping {link}: Potential redirect loop")
                            continue
                        discovered.append(link)
                        queue.append((link, depth + 1))

            self.logger.debug(f"Queue size: {len(queue)}, Discovered: {len(discovered)}")
            if self.rate_limited:
                self.logger.warning("Rate limit detected (HTTP 429). Increasing delay.")
                self.delay *= 2
                self.rate_limited = False
            await asyncio.sleep(self.delay)

        pbar.close()
        return discovered

def load_wordlist(path):
    if not os.path.isfile(path):
        logging.error(f"Wordlist not found: {path}")
        sys.exit(1)
    if os.path.getsize(path) > 100 * 1024 * 1024:
        logging.warning("Wordlist is very large. Consider using a smaller one.")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

async def generate_report(target_dir, whatweb_file, nmap_file, fuzz_file, crawl_file, fuzz_hits, crawl_results, static_assets, forms, xss_results):
    report = {
        "target": urlparse(crawl_results[0]).netloc if crawl_results else "",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "whatweb": await asyncio.to_thread(lambda: open(whatweb_file).read().strip()) if os.path.exists(whatweb_file) else "",
        "nmap": await asyncio.to_thread(lambda: open(nmap_file).read().strip()) if os.path.exists(nmap_file) else "",
        "fuzz_hits": fuzz_hits,
        "crawl_results": crawl_results,
        "static_assets": [{"url": url, "mime_type": mime} for url, mime in static_assets],
        "forms": forms,
        "xss_results": xss_results,
        "total_urls": len(fuzz_hits) + len(crawl_results) + len(static_assets)
    }
    report_file = os.path.join(target_dir, "report.json")
    await asyncio.to_thread(lambda: json.dump(report, open(report_file, 'w'), indent=2))
    return report_file

async def generate_markdown_report(json_file, output_file):
    report = await asyncio.to_thread(lambda: json.load(open(json_file, 'r')))
    target = report.get('target', 'Unknown')
    timestamp = report.get('timestamp', 'Unknown')
    whatweb = report.get('whatweb', '')
    nmap = report.get('nmap', '')
    fuzz_hits = report.get('fuzz_hits', [])
    crawl_results = report.get('crawl_results', [])
    static_assets = report.get('static_assets', [])
    forms = report.get('forms', [])
    xss_results = report.get('xss_results', [])
    total_urls = report.get('total_urls', 0)

    md_content = f"""# Pentesting Report for {target}

Generated on: {timestamp}

## Summary
- **Total URLs Discovered**: {total_urls}
- **Fuzzing Hits**: {len(fuzz_hits)}
- **Crawl Results**: {len(crawl_results)}
- **Static Assets**: {len(static_assets)}
- **Forms Found**: {len(forms)}
- **XSS Tests Performed**: {len(xss_results)}

## WhatWeb Results

{whatweb.strip() or 'No WhatWeb results available.'}

## Nmap Results

{nmap.strip() or 'No Nmap results available.'}

## Fuzzing Hits
{fuzz_hits or 'No fuzzing hits found.'}
"""
    if fuzz_hits:
        md_content += '\n'.join([f"- {url}" for url in fuzz_hits])

    md_content += "\n\n## Crawl Results\n"
    if crawl_results:
        md_content += '\n'.join([f"- {url}" for url in crawl_results])
    else:
        md_content += "No crawl results found."

    md_content += "\n\n## Static Assets\n"
    if static_assets:
        md_content += '\n'.join([f"- {asset['url']} (MIME: {asset['mime_type']})" for asset in static_assets])
    else:
        md_content += "No static assets found."

    md_content += "\n\n## Forms\n"
    if forms:
        for form in forms:
            md_content += f"- **URL**: {form['url']}\n"
            md_content += f"  - **Action**: {form['action']}\n"
            md_content += f"  - **Method**: {form['method']}\n"
            md_content += f"  - **Inputs**:\n"
            for input_field in form['inputs']:
                md_content += f"    - Name: {input_field['name']}, Type: {input_field['type']}, ID: {input_field['id']}\n"
    else:
        md_content += "No forms found."

    md_content += "\n\n## Potential XSS Vulnerabilities\n"
    if xss_results:
        for xss in xss_results:
            md_content += f"- **URL**: {xss['url']}\n"
            md_content += f"  - **Payload**: {xss['payload']}\n"
            md_content += f"  - **Status**: {xss['status']}\n"
            md_content += f"  - **Response Status**: {xss['response_status'] or 'N/A'}\n"
    else:
        md_content += "No XSS tests performed or no vulnerabilities found."

    await asyncio.to_thread(lambda: open(output_file, 'w').write(md_content))
    print(f"{Fore.GREEN}✅ Generated Markdown report → {output_file}{Style.RESET_ALL}")

async def main():
    init()
    parser = argparse.ArgumentParser(
        description="Enhanced pentesting tool: WhatWeb → optional Nmap → async crawl with fuzzing → optional Burp replay → optional XSS testing"
    )
    parser.add_argument("target", nargs="?", help="Host (e.g., example.com, www.example.com, 192.168.1.1) or URL (e.g., http://example.com)")
    parser.add_argument("--burp", action="store_true",
                        help="Replay discovered URLs through Burp proxy")
    parser.add_argument("--nocrawl", action="store_true",
                    help="Skip crawling phase entirely")
    parser.add_argument("--no-verify-ssl", action="store_true",
                        help="Disable SSL verification for HTTP requests (use with caution)")
    parser.add_argument("-w", "--wordlist", default=None,
                        help="Path to wordlist for brute forcing")
    parser.add_argument("--depth", type=int, default=1,
                        help="Max crawl depth")
    parser.add_argument("--delay", type=float, default=0.2,
                        help="Delay between requests")
    parser.add_argument("--workers", type=int, default=10,
                        help="Max concurrent requests")
    parser.add_argument("--cookies", help="Cookies for authenticated requests (e.g., 'name1=value1; name2=value2')")
    parser.add_argument("--report", action="store_true",
                        help="Generate a Markdown report from report.json")
    parser.add_argument("--report-output", default="report.md",
                        help="Output file for Markdown report (default: report.md)")
    parser.add_argument("--nonmap", action="store_true", help="Skip running Nmap after WhatWeb")
    parser.add_argument("--xss", action="store_true",
                        help="Test forms for XSS vulnerabilities with predefined payloads")
    
    parser.add_argument("--setoutput", help="Set custom output directory for scan results")
    parser.add_argument("--showoutput", action="store_true", help="Show current output directory for results")
    parser.add_argument("--setlog", help="Set custom log file path")
    parser.add_argument("--showlog", action="store_true", help="Show current log file path")
    parser.add_argument("--showxss", action="store_true", help="Show current XSS wordlist path")
    parser.add_argument("--resetxss", action="store_true", help="Reset to default built-in XSS payloads")
    parser.add_argument("--setxss", help="Set custom wordlist path for XSS testing")
    parser.add_argument("--setnmap", help="Set custom Nmap arguments (e.g. '-A -sN')")
    parser.add_argument("--shownmap", action="store_true", help="Show current Nmap arguments")
    parser.add_argument("--resetnmap", action="store_true", help="Reset Nmap arguments to default")

    args = parser.parse_args()



    if hasattr(args, "setoutput") and args.setoutput:
        custom_path = os.path.abspath(args.setoutput)
        if not os.path.isdir(custom_path):
            print(f"❌ Invalid path: {custom_path}")
            sys.exit(1)
        save_config_key("output_path", custom_path)
        print(f"✅ Output path set to: {args.setoutput}")
        sys.exit(0)

    if args.showoutput:
        print(load_config_key("output_path") or "~/.local/share/pubstomp/targets")
        sys.exit(0)


    if args.setlog:
        custom_log = os.path.abspath(os.path.expanduser(args.setlog))

        if os.path.isdir(custom_log):
            print(f"❌ '{custom_log}' is a directory. Please provide a full log file path like /path/to/pubstomp.log")
            sys.exit(1)

        save_config_key("log_path", custom_log)
        print(f"✅ Log path set to: {custom_log}")
        sys.exit(0)

    if args.showlog:
        print(load_config_key("log_path") or "~/pubstomp.log")
        sys.exit(0)


    if args.setnmap:
        save_config_key("nmap_args", args.setnmap)
        print(f"✅ Nmap arguments set to: {args.setnmap}")
        sys.exit(0)

    if args.shownmap:
        print(load_config_key("nmap_args") or "--script vuln -A")
        sys.exit(0)

    if args.resetnmap:
        save_config_key("nmap_args", None)
        print("🔄 Nmap arguments reset to default: --script vuln -A")
        sys.exit(0)

    if args.setxss:
        full_path = os.path.abspath(os.path.expanduser(args.setxss))
        if not os.path.isfile(full_path):
            print(f"❌ XSS wordlist path '{full_path}' does not exist.")
            sys.exit(1)
        save_config_key("xss_path", full_path)
        print(f"✅ XSS wordlist set to: {full_path}")
        sys.exit(0)

    if args.showxss:
        print(load_config_key("xss_path") or "Using default built-in XSS payloads.")
        sys.exit(0)

    if args.resetxss:
        save_config_key("xss_path", None)
        print("🔄 XSS wordlist reset to default payloads.")
        sys.exit(0)

    if not args.target:
        print("❌ Error: you must provide a target like 'pubstomp example.com'")
        sys.exit(1)

    log_path = load_config_key("log_path") or os.path.expanduser("~/pubstomp.log")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(os.path.expanduser(log_path), maxBytes=10*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print(f"{Fore.CYAN}📄 Logging to: {log_path}{Style.RESET_ALL}")

    parsed_target = urlparse(args.target)
    if parsed_target.scheme and parsed_target.netloc:
        target = parsed_target.netloc
        base_url = args.target
    else:
        target = args.target
        base_url = f"https://{args.target}"

    if not (validators.domain(target) or validators.ipv4(target) or validators.ipv6(target)):
        logger.error(f"Invalid target: {args.target}. Please provide a valid domain (e.g., example.com) or IP (e.g., 192.168.1.1).")
        sys.exit(1)

    host = parsed_target.netloc or target
    output_root = load_config_key("output_path") or os.path.expanduser("~/.local/share/pubstomp/targets")
    target_dir = os.path.join(output_root, host)

    target_dir = os.path.abspath(target_dir)

    os.makedirs(target_dir, exist_ok=True)

    cookies = {}
    if args.cookies:
        for cookie in args.cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value

    async with aiohttp.ClientSession(cookies=cookies, headers={'User-Agent': 'Mozilla/5.0 (compatible; SimpleSpider/1.0)'}) as session:
        try:
            async with session.head(base_url, timeout=10, allow_redirects=False, ssl=not args.no_verify_ssl) as resp:
                if resp.status in (301, 302) and 'Location' in resp.headers:
                    redirect_url = resp.headers['Location']
                    if redirect_url.startswith('https://') and urlparse(redirect_url).netloc == target:
                        logger.info(f"Detected redirect from {base_url} to {redirect_url}. Updating base_url.")
                        base_url = redirect_url
                elif resp.status >= 400:
                    logger.error(f"Target {base_url} is unreachable: HTTP {resp.status}")
                    sys.exit(1)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Target {base_url} is unreachable: {e}")
            sys.exit(1)

        whatweb_file = os.path.join(target_dir, "whatweb.txt")
        logger.info(f"Running whatweb --color=never {host}")
        print(f"{Fore.GREEN}▶️ Running whatweb --color=never {host} → {whatweb_file}{Style.RESET_ALL}")
        await asyncio.to_thread(lambda: subprocess.run(
            ["whatweb", "--color=never", host],
            stdout=open(whatweb_file, 'w'),
            stderr=subprocess.STDOUT,
            text=True))

        with open(whatweb_file) as wf:
            content = wf.read()
        ip_match = re.search(r'IP\[([^\]]+)\]', content)
        ip = ip_match.group(1) if ip_match else None

        if ip and not args.nonmap:
                nmap_file = os.path.join(target_dir, "nmap.txt")
                nmap_args = load_config_key("nmap_args") or "--script vuln -A"
                logger.info(f"Running nmap {nmap_args} -A {ip}")
                import shlex
                cmd = ["sudo", "nmap"] + shlex.split(nmap_args) + [ip]
                print(f"{Fore.GREEN}▶️ sudo nmap {nmap_args} {ip} → {nmap_file}{Style.RESET_ALL}")


                try:
                    await asyncio.to_thread(lambda: subprocess.run(
                        cmd,
                        stdout=open(nmap_file, 'w'),
                        stderr=subprocess.STDOUT,
                        text=True,
                        check=True))
                    print(f"{Fore.GREEN}✅ Nmap results → {nmap_file}{Style.RESET_ALL}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Nmap failed: {e}")

        words = await asyncio.to_thread(load_wordlist, args.wordlist) if args.wordlist else []
        fuzz_hits = []
        fuzz_file = None
        spider = SimpleSpider(
            base_url,
            max_depth=args.depth,
            delay=args.delay,
            wordlist=words,
            workers=args.workers,
            cookies=cookies,
            no_verify_ssl=args.no_verify_ssl
        )
        if words:
            logger.info(f"Fuzzing {host} with {len(words)} words")
            print(f"{Fore.GREEN}▶️ Fuzzing {host} using {args.wordlist}{Style.RESET_ALL}")
            fuzz_hits = await spider.brute_force(session)
            fuzz_file = os.path.join(target_dir, "fuzz.txt")
            await asyncio.to_thread(lambda: open(fuzz_file, 'w').writelines([url + "\n" for url in sorted(set(fuzz_hits))]))
            print(f"{Fore.GREEN}✅ Fuzz results → {fuzz_file}{Style.RESET_ALL}")
        else:
            logger.info("No wordlist provided. Skipping fuzzing.")
            print(f"{Fore.YELLOW}⚠️ No wordlist provided. Skipping fuzzing.{Style.RESET_ALL}")

        robots_paths = []
        if args.wordlist:
            robots_paths = await spider.fetch_robots(session)
            if robots_paths:
                words.extend(robots_paths)
                logger.info(f"Added {len(robots_paths)} paths from robots.txt to wordlist")
                if words and not fuzz_hits:
                    logger.info(f"Fuzzing {host} with {len(words)} words (including robots.txt)")
                    print(f"{Fore.GREEN}▶️ Fuzzing {host} with robots.txt paths{Style.RESET_ALL}")
                    fuzz_hits = await spider.brute_force(session)
                    fuzz_file = os.path.join(target_dir, "fuzz.txt")
                    await asyncio.to_thread(lambda: open(fuzz_file, 'w').writelines([url + "\n" for url in sorted(set(fuzz_hits))]))
                    print(f"{Fore.GREEN}✅ Fuzz results → {fuzz_file}{Style.RESET_ALL}")

        results = []
        if not args.nocrawl:
            results = await spider.crawl(session)
        else:
            logger.info("Skipping crawling phase due to --nocrawl flag.")
            print(f"{Fore.YELLOW}⚠️ Skipping crawling phase (--nocrawl){Style.RESET_ALL}")


        


        # Test XSS on forms if --xss flag is provided
        if args.xss and spider.forms:
            logger.info(f"Testing {len(spider.forms)} forms for XSS vulnerabilities")
            print(f"{Fore.GREEN}▶️ Testing {len(spider.forms)} forms for XSS{Style.RESET_ALL}")
            from tqdm import tqdm
            total_payloads = len(spider.forms) * len(spider.XSS_PAYLOADS)
            with tqdm(total=total_payloads, desc="XSS testing", unit="test") as xss_pbar:
                for form in spider.forms:
                    xss_form_results = await spider.test_xss_form(session, form, xss_pbar)
                    spider.xss_results.extend(xss_form_results)
            print(f"{Fore.GREEN}✅ Completed XSS testing on forms{Style.RESET_ALL}")

        all_results = sorted(set(fuzz_hits + results + [url for url, _ in spider.static_assets]))

        crawl_file = os.path.join(target_dir, "crawl.txt")
        await asyncio.to_thread(lambda: open(crawl_file, 'w').writelines([u + "\n" for u in all_results] or ["No URLs found.\n"]))
        print(f"{Fore.GREEN}✅ Saved {len(all_results)} URLs → {crawl_file}{Style.RESET_ALL}")

        assets_file = os.path.join(target_dir, "assets.txt")
        await asyncio.to_thread(lambda: open(assets_file, 'w').writelines([f"{url} (MIME: {mime})\n" for url, mime in spider.static_assets] or ["No static assets found.\n"]))
        if spider.static_assets:
            print(f"{Fore.GREEN}✅ Saved {len(spider.static_assets)} static assets → {assets_file}{Style.RESET_ALL}")

        forms_file = os.path.join(target_dir, "forms.txt")
        forms_output = []
        for form in spider.forms:
            forms_output.append(f"URL: {form['url']}")
            forms_output.append(f"  Action: {form['action']}")
            forms_output.append(f"  Method: {form['method']}")
            forms_output.append("  Inputs:")
            for input_field in form['inputs']:
                forms_output.append(f"    - Name: {input_field['name']}, Type: {input_field['type']}, ID: {input_field['id']}")
            forms_output.append("")
        await asyncio.to_thread(lambda: open(forms_file, 'w').writelines([line + "\n" for line in forms_output] or ["No forms found.\n"]))
        if spider.forms:
            print(f"{Fore.GREEN}✅ Saved {len(spider.forms)} forms → {forms_file}{Style.RESET_ALL}")

        nmap_file = os.path.join(target_dir, "nmap.txt") if os.path.exists(os.path.join(target_dir, "nmap.txt")) else ""
        report_file = await generate_report(target_dir, whatweb_file, nmap_file, fuzz_file, crawl_file, fuzz_hits, results, spider.static_assets, spider.forms, spider.xss_results)
        print(f"{Fore.GREEN}✅ Generated JSON report → {report_file}{Style.RESET_ALL}")

        if args.report:
            markdown_file = os.path.join(target_dir, args.report_output)
            await generate_markdown_report(report_file, markdown_file)
            print(f"{Fore.MAGENTA}=== Report Preview ==={Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Run 'cat {markdown_file}' to view full report{Style.RESET_ALL}")
            async def preview_markdown(file_path):
                try:
                    with open(file_path, 'r') as f:
                        lines = [next(f) for _ in range(16)]
                    for line in lines:  
                        print(line.strip())
                except (StopIteration, FileNotFoundError):
                    print(f"{Fore.RED}✖ Could not read {file_path}{Style.RESET_ALL}")
            await preview_markdown(markdown_file)
        else:


            print(f"\n{Fore.MAGENTA}=== WhatWeb Results ==={Style.RESET_ALL}")
            await asyncio.to_thread(lambda: subprocess.call(['cat', whatweb_file]))
            if fuzz_hits:
                print(f"\n{Fore.MAGENTA}=== Fuzzing Results ==={Style.RESET_ALL}")
                await asyncio.to_thread(lambda: subprocess.call(['cat', fuzz_file]))
            if spider.static_assets:
                print(f"\n{Fore.MAGENTA}=== Static Assets ==={Style.RESET_ALL}")
                await asyncio.to_thread(lambda: subprocess.call(['cat', assets_file]))
            if spider.forms:
                print(f"\n{Fore.MAGENTA}=== Forms ==={Style.RESET_ALL}")
                await asyncio.to_thread(lambda: subprocess.call(['cat', forms_file]))
            print(f"\n{Fore.MAGENTA}=== Crawl and Asset Results ==={Style.RESET_ALL}")
            await asyncio.to_thread(lambda: subprocess.call(['cat', crawl_file]))

        if args.burp:
            logger.info("Replaying through Burp proxy at 127.0.0.1:8080")
            print(f"\n{Fore.GREEN}▶️ Replaying through Burp proxy at 127.0.0.1:8080 …{Style.RESET_ALL}")
            if args.no_verify_ssl:
                logger.warning("SSL verification disabled for Burp proxy requests. This is insecure and should only be used in a controlled testing environment.")
                print(f"{Fore.YELLOW}⚠️ SSL verification disabled for Burp proxy. Use with caution in a controlled environment.{Style.RESET_ALL}")
            proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
            for u in all_results:
                try:
                    async with session.get(u, timeout=5, proxy=proxies['http'], ssl=not args.no_verify_ssl) as resp:
                        print(f"{Fore.GREEN}  • Proxied {u} (Status: {resp.status}){Style.RESET_ALL}")
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.error(f"Error proxying {u}: {e}")
                    print(f"{Fore.RED}  ✖ Error proxying {u}: {e}{Style.RESET_ALL}")
                await asyncio.sleep(args.delay)

