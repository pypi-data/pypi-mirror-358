import sys
import shutil
import logging
import subprocess
from pathlib import Path

import requests
from tqdm import tqdm
from crontab import CronTab
import time
import os

logger = logging.getLogger(__name__)

API_URL      = "https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable"
APPDIR       = Path.home() / "Applications" / "cursor"
APPIMG       = APPDIR / "cursor.AppImage"
VERFILE      = APPDIR / "version.txt"
ICON_URL     = "https://www.cursor.com/favicon.svg"
ICON_DIR     = Path.home() / ".local" / "share" / "icons"
DESKTOP_DIR  = Path.home() / ".local" / "share" / "applications"
CRON_COMMENT = "cursorcraft auto-update"

def _download(url: str, dest: Path, notify: bool = False):
    """
    Download an URL into dest:
    - if notify==False, use a tqdm bar in the terminal
    - if notify==True, use a Zenity dialog with percentage, speed & ETA
    """
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    dest.parent.mkdir(parents=True, exist_ok=True)

    zenity = shutil.which("zenity")
    use_gui = notify and zenity is not None

    if use_gui:
        # launch Zenity progress dialog
        p = subprocess.Popen([
            zenity,
            "--progress",
            "--title=Cursor Update",
            "--text=Starting download…",
            "--percentage=0",
            "--auto-close"
        ], stdin=subprocess.PIPE, text=True)
        start = time.time()
        downloaded = 0

        for chunk in resp.iter_content(chunk_size=8192):
            dest.write_bytes(dest.read_bytes() + chunk)  # stream-safe append
            downloaded += len(chunk)
            pct = int(downloaded / total * 100) if total else 0
            elapsed = time.time() - start
            speed = downloaded / elapsed if elapsed>0 else 0
            eta = (total-downloaded)/speed if speed>0 else 0
            speed_str = f"{speed/1024:.1f} KB/s"
            eta_str   = f"{eta:.0f}s"
            # update percentage + secondary text
            p.stdin.write(f"{pct}\n# {downloaded//1024} KB/{total//1024} KB @ {speed_str}, ETA {eta_str}\n")
            p.stdin.flush()

        p.stdin.close()
        p.wait()

    else:
        # fallback to tqdm in-terminal
        with open(dest, "wb") as f, tqdm(
            total=total,
            unit="B", unit_scale=True, unit_divisor=1024,
            desc=dest.name
        ) as bar:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    dest.chmod(0o755)

def cleanup_existing():
    """Remove old installs, icons, and desktop files."""
    logger.info(f"Cleaning {APPDIR}")
    if APPDIR.exists():
        shutil.rmtree(APPDIR)

    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    for d in DESKTOP_DIR.glob("*[cC]ursor*.desktop"):
        d.unlink(missing_ok=True)

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for i in ICON_DIR.glob("cursor*.svg"):
        i.unlink(missing_ok=True)

def kill_running():
    """Kill any running Cursor processes."""
    logger.info("Killing running Cursor instances")
    subprocess.run(["pkill", "-f", str(APPIMG)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fetch_info():
    """Return (version, downloadUrl) from API."""
    logger.info("Fetching API info")
    r = requests.get(API_URL)
    r.raise_for_status()
    js = r.json()
    return js["version"], js["downloadUrl"]

def install_cursor():
    """Full fresh install: cleanup → download AppImage & icon → write desktop file."""
    logger.info("=== install_cursor ===")
    cleanup_existing()
    kill_running()

    version, dl = fetch_info()

    # AppImage
    _download(dl, APPIMG)
    VERFILE.write_text(version)

    # Icon
    icon_dest = ICON_DIR / "cursor.svg"
    _download(ICON_URL, icon_dest)

    # .desktop
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    desktop = DESKTOP_DIR / "cursor.desktop"
    desktop.write_text(f"""[Desktop Entry]
Type=Application
Name=Cursor IDE
Exec={APPIMG} --no-sandbox
Icon={icon_dest}
Terminal=false
Categories=Development;IDE;
""")
    desktop.chmod(0o644)

    logger.info(f"Installed v{version}")

def update_cursor(notify: bool = False):
    """
    - If notify=False (default), shows a terminal‐only tqdm bar.
    - If notify=True (cron or explicit flag), shows a Zenity popup with speed & ETA.
    """
    if not VERFILE.exists():
        raise FileNotFoundError("No install found; run `install` first.")

    kill_running()
    current = VERFILE.read_text().strip()
    latest, dl = fetch_info()

    # temporarily disable the desktop launcher
    entry  = DESKTOP_DIR / "cursor.desktop"
    backup = DESKTOP_DIR / "cursor.desktop.disabled"
    if entry.exists():
        entry.rename(backup)

    changed = False
    if current != latest:
        _download(dl, APPIMG, notify=notify)
        VERFILE.write_text(latest)
        changed = True

    # restore desktop launcher
    if backup.exists():
        backup.rename(entry)

    return changed

def enable_auto_update(cron_time: str = "* 5 * * *"):
    """Schedule `update --notify` via cron."""
    logger.info(f"Scheduling auto-update ({cron_time})")
    cron = CronTab(user=True)
    cron.remove_all(comment=CRON_COMMENT)
    env = (
        f"DISPLAY=:0 "
        f"XDG_RUNTIME_DIR=/run/user/{os.getuid()} "
        f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{os.getuid()}/bus "
    )
    job = cron.new(
        command=env + f"{sys.executable} -m cursorcraft.cli update --notify",
        comment=CRON_COMMENT
    )
    job.setall(cron_time)
    cron.write()
    logger.info("Cron job installed.")

def disable_auto_update():
    """Remove any auto-update cron job."""
    logger.info("Removing auto-update cron job")
    cron = CronTab(user=True)
    cron.remove_all(comment=CRON_COMMENT)
    cron.write()
    logger.info("Removed cron job.")