# -*- coding: utf-8 -*-
"""
CF Xray IP Benchmark — Apple-inspired desktop GUI
=================================================
Design language: clean cards, soft depth, system typography, accent blue.
Works on Windows / macOS / Linux with stock Tkinter.

Run:  python gui_app.py
  or: gui.bat
"""

from __future__ import annotations

import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Entry, Text, Canvas, Checkbutton,
    BooleanVar, StringVar, IntVar, filedialog, messagebox, END,
    DISABLED, NORMAL, WORD, BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM,
)
from tkinter import ttk

SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# ---------------------------------------------------------------------------
# Apple-inspired palette (light + subtle depth)
# ---------------------------------------------------------------------------
C = {
    "bg":        "#F5F5F7",       # window chrome
    "surface":   "#FFFFFF",       # cards
    "surface2":  "#FBFBFD",
    "border":    "#E5E5EA",
    "text":      "#1D1D1F",
    "text2":     "#6E6E73",
    "text3":     "#8E8E93",
    "blue":      "#007AFF",
    "blue_press":"#0062CC",
    "blue_soft": "#E8F1FF",
    "green":     "#34C759",
    "red":       "#FF3B30",
    "orange":    "#FF9F0A",
    "fill":      "#F2F2F7",
    "log_bg":    "#1C1C1E",
    "log_fg":    "#F5F5F7",
}

FONT = ("Segoe UI", 11)
FONT_SM = ("Segoe UI", 10)
FONT_B = ("Segoe UI Semibold", 11)
FONT_TITLE = ("Segoe UI Semibold", 20)
FONT_SECTION = ("Segoe UI Semibold", 13)
FONT_MONO = ("Cascadia Mono", 9)
if sys.platform == "darwin":
    FONT = ("SF Pro Text", 12)
    FONT_SM = ("SF Pro Text", 11)
    FONT_B = ("SF Pro Text", 12, "bold")
    FONT_TITLE = ("SF Pro Display", 22, "bold")
    FONT_SECTION = ("SF Pro Text", 13, "bold")
    FONT_MONO = ("SF Mono", 10)


def card(parent, **kw) -> Frame:
    f = Frame(parent, bg=C["surface"], highlightbackground=C["border"],
              highlightthickness=1, **kw)
    return f


class PillButton(Frame):
    """Rounded-looking primary / secondary button."""

    def __init__(self, parent, text, command, primary=True, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self.command = command
        self.primary = primary
        self._enabled = True
        bg = C["blue"] if primary else C["fill"]
        fg = "#FFFFFF" if primary else C["text"]
        self.btn = Label(
            self, text=text, bg=bg, fg=fg, font=FONT_B,
            padx=18, pady=8, cursor="hand2",
        )
        self.btn.pack()
        self.btn.bind("<Button-1>", self._click)
        self.btn.bind("<Enter>", self._enter)
        self.btn.bind("<Leave>", self._leave)

    def _click(self, _=None):
        if self._enabled and self.command:
            self.command()

    def _enter(self, _):
        if not self._enabled:
            return
        self.btn.configure(bg=C["blue_press"] if self.primary else C["border"])

    def _leave(self, _):
        if not self._enabled:
            return
        self.btn.configure(bg=C["blue"] if self.primary else C["fill"])

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self.btn.configure(
                bg=C["blue"] if self.primary else C["fill"],
                fg="#FFFFFF" if self.primary else C["text"],
                cursor="hand2",
            )
        else:
            self.btn.configure(bg=C["border"], fg=C["text3"], cursor="arrow")


class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("CF Xray IP Benchmark")
        self.root.geometry("1020x760")
        self.root.minsize(900, 640)
        self.root.configure(bg=C["bg"])
        try:
            self.root.tk.call("tk", "scaling", 1.15)
        except Exception:
            pass

        self.proc = None
        self.running = False
        self._config_backup = None

        self.var_cfip = StringVar(value=str(SCRIPT_DIR / "cfip.txt"))
        self.var_links = StringVar(value=str(SCRIPT_DIR / "links.txt"))
        self.var_config = StringVar(value=str(SCRIPT_DIR / "config.json"))
        self.var_workers = IntVar(value=1)
        self.var_max_ips = IntVar(value=0)
        self.var_clear_temp = BooleanVar(value=False)
        self.var_baseline = BooleanVar(value=True)
        self.var_report = StringVar(value="")
        self.status = StringVar(value="Ready")

        self._load_defaults()
        self._build()

    def _load_defaults(self):
        cfg_path = SCRIPT_DIR / "config.json"
        if not cfg_path.exists():
            return
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.var_workers.set(int(cfg.get("workers", 1) or 1))
            self.var_max_ips.set(int(cfg.get("max_ips", 0) or 0))
            ct = cfg.get("clear_temp")
            if isinstance(ct, bool):
                self.var_clear_temp.set(ct)
            base = cfg.get("baseline", {})
            if isinstance(base, dict):
                self.var_baseline.set(bool(base.get("enabled", True)))
            self.var_report.set(str(cfg.get("report_name", "") or ""))
        except Exception:
            pass

    # ------------------------------------------------------------------ UI
    def _build(self):
        # Top bar
        top = Frame(self.root, bg=C["bg"], pady=18, padx=28)
        top.pack(side=TOP, fill=X)
        Label(top, text="CF Xray IP Benchmark", bg=C["bg"], fg=C["text"],
              font=FONT_TITLE).pack(side=LEFT)
        Label(top, text="Cloudflare · Xray · Speed", bg=C["bg"], fg=C["text3"],
              font=FONT_SM).pack(side=LEFT, padx=(12, 0), pady=(6, 0))
        Label(top, textvariable=self.status, bg=C["bg"], fg=C["text2"],
              font=FONT_SM).pack(side=RIGHT, pady=(6, 0))

        # Scrollable-ish body
        body = Frame(self.root, bg=C["bg"], padx=28)
        body.pack(side=TOP, fill=BOTH, expand=True)

        # Files card
        self._section_title(body, "Files")
        files = card(body, padx=16, pady=14)
        files.pack(fill=X, pady=(0, 14))
        self._path_row(files, "CF IP list", self.var_cfip)
        self._path_row(files, "Config links", self.var_links)
        self._path_row(files, "Settings", self.var_config)

        # Options card
        self._section_title(body, "Options")
        opts = card(body, padx=16, pady=14)
        opts.pack(fill=X, pady=(0, 14))

        row = Frame(opts, bg=C["surface"])
        row.pack(fill=X, pady=(0, 10))
        self._spin(row, "Workers", self.var_workers, 1, 16)
        self._spin(row, "Max IPs (0 = all)", self.var_max_ips, 0, 10000)
        Label(row, text="Report", bg=C["surface"], fg=C["text2"], font=FONT_SM).pack(
            side=LEFT, padx=(8, 6))
        self._entry(row, self.var_report, width=16)

        row2 = Frame(opts, bg=C["surface"])
        row2.pack(fill=X)
        self._check(row2, "Clear temp after run", self.var_clear_temp)
        self._check(row2, "Baseline internet test", self.var_baseline)

        # Actions
        actions = Frame(body, bg=C["bg"], pady=4)
        actions.pack(fill=X, pady=(0, 12))
        self.btn_start = PillButton(actions, "Start Benchmark", self.start, primary=True)
        self.btn_start.pack(side=LEFT)
        self.btn_stop = PillButton(actions, "Stop", self.stop, primary=False)
        self.btn_stop.pack(side=LEFT, padx=(10, 0))
        self.btn_stop.set_enabled(False)

        PillButton(actions, "Results", self.open_results, primary=False).pack(side=LEFT, padx=(10, 0))
        PillButton(actions, "Edit Config", lambda: self._open(self.var_config.get()), primary=False).pack(
            side=LEFT, padx=(10, 0))
        PillButton(actions, "Debug One", self.run_debug, primary=False).pack(side=LEFT, padx=(10, 0))

        # Progress
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Apple.Horizontal.TProgressbar",
            troughcolor=C["fill"], background=C["blue"],
            bordercolor=C["fill"], lightcolor=C["blue"], darkcolor=C["blue"],
            thickness=4,
        )
        self.progress = ttk.Progressbar(body, mode="indeterminate", style="Apple.Horizontal.TProgressbar")
        self.progress.pack(fill=X, pady=(0, 12))

        # Log card
        self._section_title(body, "Live Output")
        log_card = card(body, padx=2, pady=2)
        log_card.pack(fill=BOTH, expand=True, pady=(0, 20))

        log_wrap = Frame(log_card, bg=C["log_bg"])
        log_wrap.pack(fill=BOTH, expand=True, padx=1, pady=1)
        self.log = Text(
            log_wrap, bg=C["log_bg"], fg=C["log_fg"], insertbackground=C["log_fg"],
            relief="flat", font=FONT_MONO, wrap=WORD, state=DISABLED,
            padx=14, pady=12, borderwidth=0, highlightthickness=0,
        )
        scroll = ttk.Scrollbar(log_wrap, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.log.pack(side=LEFT, fill=BOTH, expand=True)

        self.log.tag_configure("ok", foreground="#30D158")
        self.log.tag_configure("err", foreground="#FF453A")
        self.log.tag_configure("warn", foreground="#FFD60A")
        self.log.tag_configure("info", foreground="#64D2FF")
        self.log.tag_configure("dim", foreground="#8E8E93")

    def _section_title(self, parent, text):
        Label(parent, text=text, bg=C["bg"], fg=C["text"], font=FONT_SECTION).pack(
            anchor="w", pady=(0, 8))

    def _path_row(self, parent, label, var):
        row = Frame(parent, bg=C["surface"])
        row.pack(fill=X, pady=4)
        Label(row, text=label, bg=C["surface"], fg=C["text2"], font=FONT_SM, width=12, anchor="w").pack(
            side=LEFT)
        e = Entry(
            row, textvariable=var, bg=C["fill"], fg=C["text"], insertbackground=C["text"],
            relief="flat", font=FONT_SM, highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["blue"],
        )
        e.pack(side=LEFT, fill=X, expand=True, padx=8, ipady=6)
        b = Label(row, text="Browse", bg=C["fill"], fg=C["blue"], font=FONT_B,
                  padx=12, pady=6, cursor="hand2")
        b.pack(side=LEFT)
        b.bind("<Button-1>", lambda _e, v=var: self._browse(v))

    def _entry(self, parent, var, width=12):
        e = Entry(
            parent, textvariable=var, width=width, bg=C["fill"], fg=C["text"],
            insertbackground=C["text"], relief="flat", font=FONT_SM,
            highlightthickness=1, highlightbackground=C["border"], highlightcolor=C["blue"],
        )
        e.pack(side=LEFT, ipady=5)
        return e

    def _spin(self, parent, label, var, frm, to):
        Label(parent, text=label, bg=C["surface"], fg=C["text2"], font=FONT_SM).pack(
            side=LEFT, padx=(0, 6))
        sp = ttk.Spinbox(parent, from_=frm, to=to, textvariable=var, width=6, font=FONT_SM)
        sp.pack(side=LEFT, padx=(0, 16))

    def _check(self, parent, text, var):
        Checkbutton(
            parent, text=text, variable=var, bg=C["surface"], fg=C["text"],
            selectcolor=C["fill"], activebackground=C["surface"], activeforeground=C["text"],
            font=FONT_SM, highlightthickness=0, bd=0,
        ).pack(side=LEFT, padx=(0, 18))

    def _browse(self, var):
        path = filedialog.askopenfilename(
            initialdir=str(SCRIPT_DIR),
            filetypes=[("Text/JSON", "*.txt *.json"), ("All", "*.*")],
        )
        if path:
            var.set(path)

    def _open(self, path: str):
        p = Path(path)
        if not p.exists():
            messagebox.showwarning("Missing", f"Not found:\n{path}")
            return
        try:
            os.startfile(str(p))  # type: ignore
        except Exception:
            subprocess.Popen(["xdg-open", str(p)])

    def open_results(self):
        d = SCRIPT_DIR / "results"
        d.mkdir(exist_ok=True)
        try:
            os.startfile(str(d))  # type: ignore
        except Exception:
            subprocess.Popen(["xdg-open", str(d)])

    # ------------------------------------------------------------------ log
    def append_log(self, line: str):
        low = line.lower()
        tag = None
        if "[ ok ]" in low or "status : ok" in low or line.strip().startswith("[OK]"):
            tag = "ok"
        elif "[err" in low or "fail (" in low or "error" in low:
            tag = "err"
        elif "[warn" in low or "skip" in low:
            tag = "warn"
        elif "[info" in low or line.strip().startswith("..."):
            tag = "info"

        def _write():
            self.log.configure(state=NORMAL)
            self.log.insert(END, line + "\n", tag if tag else ())
            self.log.see(END)
            self.log.configure(state=DISABLED)

        self.root.after(0, _write)

    def set_status(self, text: str):
        self.root.after(0, lambda: self.status.set(text))

    # ------------------------------------------------------------------ run
    def _patch_config(self) -> bool:
        src = Path(self.var_config.get())
        if not src.exists():
            src = SCRIPT_DIR / "config.json"
        try:
            cfg = json.loads(src.read_text(encoding="utf-8")) if src.exists() else {}
        except Exception as e:
            messagebox.showerror("Config", str(e))
            return False

        cfg["workers"] = int(self.var_workers.get())
        cfg["max_ips"] = int(self.var_max_ips.get())
        cfg["clear_temp"] = bool(self.var_clear_temp.get())
        cfg["report_name"] = self.var_report.get().strip()
        cfg.setdefault("baseline", {})
        if isinstance(cfg["baseline"], dict):
            cfg["baseline"]["enabled"] = bool(self.var_baseline.get())
        cfg.setdefault("paths", {})
        if isinstance(cfg["paths"], dict):
            for key, var in (("cfip_file", self.var_cfip), ("links_file", self.var_links)):
                src_file = Path(var.get())
                if src_file.exists() and src_file.resolve().parent != SCRIPT_DIR.resolve():
                    dest = SCRIPT_DIR / f"_gui_{src_file.name}"
                    dest.write_text(src_file.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                    cfg["paths"][key] = dest.name
                else:
                    cfg["paths"][key] = src_file.name if src_file.exists() else cfg["paths"].get(key, src_file.name)

        main_cfg = SCRIPT_DIR / "config.json"
        try:
            if main_cfg.exists():
                self._config_backup = main_cfg.read_text(encoding="utf-8")
            main_cfg.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Config", f"Cannot write config: {e}")
            return False
        return True

    def _restore_config(self):
        try:
            if self._config_backup is not None:
                (SCRIPT_DIR / "config.json").write_text(self._config_backup, encoding="utf-8")
        except Exception:
            pass

    def start(self):
        if self.running:
            return
        if not Path(self.var_cfip.get()).exists():
            messagebox.showerror("Missing", "CF IP file not found")
            return
        if not Path(self.var_links.get()).exists():
            messagebox.showerror("Missing", "Links file not found")
            return
        if not self._patch_config():
            return

        self.log.configure(state=NORMAL)
        self.log.delete("1.0", END)
        self.log.configure(state=DISABLED)

        self.running = True
        self.btn_start.set_enabled(False)
        self.btn_stop.set_enabled(True)
        self.progress.start(14)
        self.set_status("Running…")

        args = [
            sys.executable, "-u", str(SCRIPT_DIR / "cf_xray_benchmark.py"),
            f"workers={int(self.var_workers.get())}",
            f"clear_temp={'true' if self.var_clear_temp.get() else 'false'}",
        ]
        if int(self.var_max_ips.get()) > 0:
            args.append(f"max_ips={int(self.var_max_ips.get())}")
        if self.var_report.get().strip():
            args.append(f"report={self.var_report.get().strip()}")

        def run():
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "xray.exe"],
                        capture_output=True,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"
                self.proc = subprocess.Popen(
                    args, cwd=str(SCRIPT_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1, env=env,
                    creationflags=creationflags,
                )
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self.append_log(line.rstrip("\n"))
                self.proc.wait()
                if self.proc.returncode == 0:
                    self.append_log("[OK] Benchmark finished.")
                    self.set_status("Done")
                else:
                    self.append_log(f"[ERR] Exit code {self.proc.returncode}")
                    self.set_status(f"Failed ({self.proc.returncode})")
            except Exception as e:
                self.append_log(f"[ERR] {e}")
                self.set_status("Error")
            finally:
                self._restore_config()
                self.root.after(0, self._finish_ui)

        threading.Thread(target=run, daemon=True).start()

    def _finish_ui(self):
        self.running = False
        self.proc = None
        self.progress.stop()
        self.btn_start.set_enabled(True)
        self.btn_stop.set_enabled(False)

    def stop(self):
        if not self.running:
            return
        self.append_log("[WARN] Stopping…")
        self.set_status("Stopping…")
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except Exception:
                    self.proc.kill()
        except Exception:
            pass
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/IM", "xray.exe"], capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

    def run_debug(self):
        if self.running:
            messagebox.showinfo("Busy", "Stop the benchmark first.")
            return
        debug = SCRIPT_DIR / "debug_one.py"
        if not debug.exists():
            messagebox.showerror("Missing", "debug_one.py not found")
            return
        self.log.configure(state=NORMAL)
        self.log.delete("1.0", END)
        self.log.configure(state=DISABLED)
        self.running = True
        self.btn_start.set_enabled(False)
        self.btn_stop.set_enabled(True)
        self.progress.start(14)
        self.set_status("Debug running…")

        def run():
            try:
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                self.proc = subprocess.Popen(
                    [sys.executable, "-u", str(debug)], cwd=str(SCRIPT_DIR),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    encoding="utf-8", errors="replace", bufsize=1, env=env,
                    creationflags=creationflags,
                )
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self.append_log(line.rstrip("\n"))
                self.proc.wait()
                self.set_status("Debug done" if self.proc.returncode == 0 else "Debug failed")
            except Exception as e:
                self.append_log(f"[ERR] {e}")
                self.set_status("Error")
            finally:
                self.root.after(0, self._finish_ui)

        threading.Thread(target=run, daemon=True).start()


def main():
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
