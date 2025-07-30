import os
import sys
import threading
import subprocess
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import shutil

import json

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


def check_python_deps():
    missing = []
    for mod in ["aiohttp", "validators", "colorama", "tqdm", "bs4"]:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    return missing


def check_external_tools(include_nmap=True):
    tools = ["whatweb"]
    if include_nmap:
        tools.append("nmap")
    return [t for t in tools if shutil.which(t) is None]


class PubStompGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PubStomp GUI")
        self.geometry("900x700")

        self.output_root = load_config_key("output_path") or os.path.expanduser("~/.local/share/pubstomp/targets")
        os.makedirs(self.output_root, exist_ok=True)
        self.current_target_dir = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_scan_tab()
        self._build_report_tab()
        self._build_targets_tab()
        self.refresh_targets()

    def _build_scan_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Scan")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Target:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(frame)
        self.target_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Nmap Args:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.nmap_entry = ttk.Entry(frame)
        self.nmap_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.nmap_entry.insert(0, load_config_key("nmap_args") or "--script vuln -A")

        ttk.Label(frame, text="Wordlist:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.wordlist_entry = ttk.Entry(frame)
        self.wordlist_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self._browse_wordlist).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(frame, text="XSS Wordlist:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.xss_entry = ttk.Entry(frame)
        self.xss_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self._browse_xss).grid(row=3, column=2, padx=5, pady=5)
        self.xss_entry.insert(0, load_config_key("xss_path") or "")

        self.enable_xss = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Enable XSS Testing", variable=self.enable_xss).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.run_nmap = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Run Nmap", variable=self.run_nmap).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.burp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Use Burp Proxy", variable=self.burp_var).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.nocrawl_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Skip Crawling", variable=self.nocrawl_var).grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.no_verify_ssl_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Disable SSL Verification", variable=self.no_verify_ssl_var).grid(row=6, column=0, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Depth:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.depth_var = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=self.depth_var, width=5).grid(row=7, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Delay:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.delay_var = tk.DoubleVar(value=0.2)
        ttk.Entry(frame, textvariable=self.delay_var, width=5).grid(row=8, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Workers:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.workers_var = tk.IntVar(value=10)
        ttk.Entry(frame, textvariable=self.workers_var, width=5).grid(row=9, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Cookies:").grid(row=10, column=0, sticky="w", padx=5, pady=5)
        self.cookies_entry = ttk.Entry(frame)
        self.cookies_entry.grid(row=10, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(frame, text="Start Scan", command=self.start_scan).grid(row=11, column=0, padx=5, pady=10)

        self.progress = scrolledtext.ScrolledText(frame, height=25)
        self.progress.grid(row=12, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        frame.rowconfigure(12, weight=1)

    def _build_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Report")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.report_text = scrolledtext.ScrolledText(frame)
        self.report_text.grid(row=0, column=0, sticky="nsew")

    def _build_targets_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Targets")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.targets_list = tk.Listbox(frame)
        self.targets_list.grid(row=0, column=0, sticky="nsew")
        self.targets_list.bind("<<ListboxSelect>>", self._on_select_target)
        ttk.Button(frame, text="Refresh", command=self.refresh_targets).grid(row=1, column=0, pady=5)

    def _browse_wordlist(self):
        path = filedialog.askopenfilename()
        if path:
            self.wordlist_entry.delete(0, tk.END)
            self.wordlist_entry.insert(0, path)

    def _browse_xss(self):
        path = filedialog.askopenfilename()
        if path:
            self.xss_entry.delete(0, tk.END)
            self.xss_entry.insert(0, path)

    def refresh_targets(self):
        self.targets_list.delete(0, tk.END)
        if os.path.isdir(self.output_root):
            for name in sorted(os.listdir(self.output_root)):
                if os.path.isdir(os.path.join(self.output_root, name)):
                    self.targets_list.insert(tk.END, name)

    def _on_select_target(self, event):
        if not self.targets_list.curselection():
            return
        name = self.targets_list.get(self.targets_list.curselection()[0])
        self.current_target_dir = os.path.join(self.output_root, name)
        self.load_report()
        self.notebook.select(1)  # switch to report tab

    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            return
        missing = check_python_deps()
        if missing:
            messagebox.showerror(
                "Missing Python packages",
                "Install required packages: " + ", ".join(missing)
            )
            return
        tool_missing = check_external_tools(include_nmap=self.run_nmap.get())
        if tool_missing:
            messagebox.showerror(
                "Missing tools",
                "These external commands are required: " + ", ".join(tool_missing)
            )
            return
        save_config_key("nmap_args", self.nmap_entry.get().strip())
        xss_path = self.xss_entry.get().strip()
        if xss_path:
            save_config_key("xss_path", xss_path)
        # Prefer invoking the CLI module directly so the GUI works whether
        # PubStomp is installed as a package or run from source.
        cmd = ["pubstomp", target, "--report"]
        if self.wordlist_entry.get().strip():
            cmd += ["--wordlist", self.wordlist_entry.get().strip()]
        if self.enable_xss.get():
            cmd += ["--xss"]
        if not self.run_nmap.get():
            cmd += ["--nonmap"]
        if self.burp_var.get():
            cmd += ["--burp"]
        if self.nocrawl_var.get():
            cmd += ["--nocrawl"]
        if self.no_verify_ssl_var.get():
            cmd += ["--no-verify-ssl"]
        cmd += ["--depth", str(self.depth_var.get())]
        cmd += ["--delay", str(self.delay_var.get())]
        cmd += ["--workers", str(self.workers_var.get())]
        if self.cookies_entry.get().strip():
            cmd += ["--cookies", self.cookies_entry.get().strip()]
        thread = threading.Thread(target=self._run_process, args=(cmd, target), daemon=True)
        thread.start()

    def _run_process(self, cmd, target):
        self.progress.delete("1.0", tk.END)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self.progress.insert(tk.END, line)
            self.progress.see(tk.END)
        proc.wait()
        if proc.returncode != 0:
            messagebox.showerror("Scan failed", f"Command exited with status {proc.returncode}. Check output for details.")
        host = urlparse(target).netloc or target
        self.current_target_dir = os.path.join(self.output_root, host)
        self.load_report()
        self.refresh_targets()

    def load_report(self):
        if not self.current_target_dir:
            return
        report_file = os.path.join(self.current_target_dir, "report.md")
        self.report_text.delete("1.0", tk.END)
        if os.path.exists(report_file):
            with open(report_file, "r", encoding="utf-8", errors="ignore") as f:
                self.report_text.insert(tk.END, f.read())
        else:
            self.report_text.insert(tk.END, "No report found.")


def main():
    app = PubStompGUI()
    app.mainloop()


if __name__ == "__main__":
    main()