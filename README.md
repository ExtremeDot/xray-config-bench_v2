# CF Xray IP Benchmark

Test **Cloudflare IPs** with your **Xray share-links** (`vless` / `vmess` / `trojan`), score them for **Web**, **Instagram**, and **Gaming**, and export ranked results to Excel.

Inspired by [ExtremeDot/xray-config-benchmark](https://github.com/ExtremeDot/xray-config-benchmark), focused on CF IP swapping, early filtering of dead IPs, and real-world relay checks.

---

## Features

- Swap each CF IP into your config and test through a local Xray SOCKS5 proxy
- **Quick probe filter** — skip dead or ultra-slow IPs before full tests (default max ping **2000 ms**)
- **Baseline** test of your real internet (no VPN) for side-by-side comparison
- Latency / Download / Upload via Cloudflare speed endpoints
- Relay open-time to Google, YouTube, Instagram, GitHub, Cloudflare, Microsoft
- Scores **0–10** for Web, Instagram, Gaming + Overall
- Top-N ranking tables (ASCII) + Excel export + live log
- `config.json` toggles for almost every step
- **Apple-inspired GUI** (Windows / Linux / macOS, Tkinter only)
- CLI + `setup` / `run` scripts for Windows and Linux

---

## Quick start

### Windows

```bat
setup.bat
run.bat
```

**GUI (recommended):**

```bat
gui.bat
```

or:

```bat
python gui.py
```

Light card UI, system fonts, Apple accent blue. No extra GUI packages (uses built-in Tkinter).

### Linux / macOS

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

GUI:

```bash
python3 gui.py
```

### Manual

```bash
pip install -r requirements.txt
python cf_xray_benchmark.py
```

---

## Project layout

```text
cf-xray-benchmark/
  cf_xray_benchmark.py   # main CLI benchmark
  debug_one.py           # single-config debug (no IP swap)
  gui.py                 # GUI launcher
  gui_app.py             # Apple-inspired GUI
  gui.bat                # Windows GUI shortcut
  config.json            # all toggles (documented)
  cfip.txt               # IPs / CIDRs / domains
  links.txt              # share-links
  requirements.txt
  setup.bat / setup.sh   # install dependencies
  run.bat / run.sh       # run CLI with defaults
  README.md
  temp/                  # runtime Xray JSON configs
  results/               # Excel reports
  logs/                  # live logs
```

---

## Files you must prepare

### `links.txt`

One share-link per line:

```text
vless://uuid@host:443?security=tls&type=ws&path=/&sni=example.com#MyConfig
# comments are ok
```

Supported protocols: `vless://` · `vmess://` · `trojan://`

### `cfip.txt`

One entry per line. Supported formats:

```text
# scanner style (download_ping - upload_ping - IP)
1181 - 0 - 172.66.170.97

# plain IPv4
172.66.45.96

# CIDR (expanded to hosts; large nets capped at 4096)
172.66.170.0/24

# domain (resolved via DNS A records)
cdn.example.com

# comments
# ignored
```

---

## How a test works

For each CF IP + config:

1. Build a temporary Xray config (address replaced with the CF IP)
2. Start local SOCKS on a free port
3. **Quick probe** (short timeout) — if unreachable or ping **> `filter.max_latency_ms`** → `SKIP` (no full tests)
4. Full latency samples
5. Download / upload (if enabled)
6. Relay pings to major sites (if enabled)
7. Score Web / Instagram / Gaming / Overall (0–10)

At the start (optional): **baseline** measures your direct line without any proxy.

At the end: Top-N tables per category, comparison vs baseline, Excel + log.

---

## Configuration (`config.json`)

Keys starting with `_` are comments only and are ignored by the app.

| Section | Purpose |
|---------|---------|
| `workers` | Parallel tests (start with `1` on Windows) |
| `max_ips` | Cap number of IPs (`0` = all) |
| `report_name` | Prefix for Excel/log filenames |
| `clear_temp` | `true` / `false` / `null` (ask at end) |
| `display.*` | Progress lines, live results, log file |
| `baseline.enabled` | Direct internet test before proxies |
| `filter.enabled` | Quick probe + early skip |
| `filter.max_latency_ms` | Skip if first ping above this (default **2000**) |
| `filter.quick_timeout_seconds` | Probe timeout (default **3**) |
| `filter.require_exit_ip` | Skip when exit IP cannot be read |
| `tests.latency/download/upload` | Enable + samples / payload size / rounds |
| `relay.enabled` + `relay.sites.*` | Per-site on/off + URL |
| `scoring.web/instagram/gaming` | Category scores on/off |
| `scoring.overall_weights` | Weights for Overall (normalized) |
| `ranking.top_n` | Rows in each Top table |
| `ranking.show_*_top` | Show/hide each Top table |
| `ranking.compare_with_baseline` | `vs Direct` column |
| `timeouts.http_seconds` | HTTP timeout for full tests |
| `timeouts.xray_startup_seconds` | Wait for local SOCKS |
| `paths.*` | Filenames and folders |
| `excel.enabled` | Write `results/*.xlsx` |

### Example: faster run, strict filter

```json
"workers": 2,
"max_ips": 30,
"filter": {
  "enabled": true,
  "max_latency_ms": 1500,
  "quick_timeout_seconds": 3
},
"baseline": { "enabled": true },
"relay": { "enabled": false },
"ranking": { "top_n": 10 }
```

### Example: only latency + web

```json
"tests": {
  "latency": { "enabled": true, "samples": 5 },
  "download": { "enabled": true, "bytes": 250000, "rounds": 1 },
  "upload": { "enabled": false }
},
"scoring": {
  "web": true,
  "instagram": false,
  "gaming": false
},
"ranking": {
  "show_instagram_top": false,
  "show_gaming_top": false
}
```

---

## CLI

CLI arguments **override** `config.json` when provided:

```bash
python cf_xray_benchmark.py
python cf_xray_benchmark.py workers=2 max_ips=15 clear_temp=false report=myrun
python cf_xray_benchmark.py custom
```

| Argument | Meaning |
|----------|---------|
| `workers=N` | Concurrent tests |
| `max_ips=N` | Only first N targets from `cfip.txt` |
| `report=NAME` | Filename prefix |
| `clear_temp=true\|false` | Delete or keep `temp/` |
| `custom` | Interactive prompts at start |

---

## GUI

```bat
gui.bat
```

```bash
python gui.py
```

| Control | Action |
|---------|--------|
| Files | Paths to `cfip.txt`, `links.txt`, `config.json` |
| Workers / Max IPs / Report | Same as CLI |
| Clear temp / Baseline | Toggles |
| Start / Stop | Run or abort benchmark |
| Results | Open `results/` folder |
| Edit Config | Open `config.json` |
| Debug One | Run `debug_one.py` |
| Live Output | Colorized streaming log |

Design: light Apple-style cards, accent `#007AFF`, dark log panel. Implemented in `gui_app.py`.

---

## Debug one config (no IP swap)

If the main tool fails, verify the link first:

```bash
python debug_one.py
python debug_one.py "vless://uuid@host:443?..."
```

Uses the first non-comment line in `links.txt` unless a link is passed on the command line.

### Windows: leftover xray processes

```powershell
Get-Process xray -ErrorAction SilentlyContinue | Stop-Process -Force
```

`run.bat` / the GUI also try to kill `xray.exe` before starting.

---

## Output

| Path | Content |
|------|---------|
| `results/*.xlsx` | Full results + ranking sheets |
| `logs/*.log` | Live log of the run |
| `temp/` | Per-test Xray JSON (and `FAILED_*.json` on errors) |

### Scores (0–10)

| Range | Meaning |
|-------|---------|
| 9–10 | Excellent |
| 7–8 | Good |
| 5–6 | Average |
| 3–4 | Weak |
| 0–2 | Poor |

**Overall** = weighted mix of Web + Instagram + Gaming (weights in `config.json`).

Final screen also shows:

- Your direct baseline (if enabled)
- Top N for Web / Instagram / Gaming / Overall
- Best IP per category
- Proxy download as % of direct speed

---

## Requirements

- Python **3.9+**
- Packages in `requirements.txt`:

```text
requests[socks]
openpyxl
colorama
```

- `xray` / `xray.exe` (downloaded automatically if missing)
- Network access to Cloudflare speed endpoints and relay sites

---

## Tips

1. Start with **`workers=1`** on Windows; raise only after it is stable.
2. Allowlist `python.exe` and `xray.exe` in antivirus if starts are slow or blocked.
3. Use **`filter.max_latency_ms`** (e.g. 1500–2000) so bad IPs are skipped quickly.
4. Large CIDRs are expanded but capped; use `max_ips` to limit further.
5. Keep `clear_temp=false` while debugging so you can inspect `temp/FAILED_*.json`.

---

## License / credit

Benchmark approach inspired by [ExtremeDot/xray-config-benchmark](https://github.com/ExtremeDot/xray-config-benchmark).  
Xray core: [XTLS/Xray-core](https://github.com/XTLS/Xray-core).
