import sys
import logging
import shutil
import subprocess
from pathlib import Path

import click
from cursorcraft import (
    install_cursor,
    update_cursor,
    enable_auto_update,
    disable_auto_update
)

# Configure console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

def ensure_system_packages():
    """Auto-install zenity & notify-send if missing."""
    deps = []
    if shutil.which("zenity") is None:
        deps.append("zenity")
    if shutil.which("notify-send") is None:
        deps.append("libnotify-bin")
    if deps:
        click.secho(f"🔧 Installing system deps: {' '.join(deps)}", fg="yellow")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y"] + deps, check=True)
        click.secho("✅ Installed system deps", fg="green")

@click.group()
@click.version_option(prog_name="cursorcraft")
def main():
    """cursorcraft — install, update, and auto-update Cursor IDE."""
    pass

@main.command()
def install():
    """Install Cursor (fresh)."""
    ensure_system_packages()
    try:
        install_cursor()
        click.secho("✅ Installed Cursor (terminal-only progress).", fg="green")
    except Exception as e:
        click.secho(f"❌ Install failed: {e}", fg="red")
        sys.exit(1)

@main.command()
@click.option("--notify", is_flag=True, help="Send desktop notifications (for cron jobs)")
def update(notify):
    """Manually update Cursor."""
    ensure_system_packages()

    if notify:
        subprocess.run(["notify-send", "Cursor Updater", "Checking for updates…"], check=False)

    try:
        changed = update_cursor(notify=notify)
        verfile = Path.home() / "Applications" / "cursor" / "version.txt"
        current = verfile.read_text().strip()
        if changed:
            click.secho(f"✅ Updated to v{current}.", fg="green")
            if notify:
                subprocess.run(
                    ["notify-send", "Cursor Updater", f"Updated to v{current}"], check=False
                )
        else:
            click.secho("ℹ️  Already up-to-date.", fg="yellow")
            if notify:
                subprocess.run(
                    ["notify-send", "Cursor Updater", f"Already v{current}"], check=False
                )
    except FileNotFoundError as e:
        click.secho(f"❌ {e}", fg="red")
        sys.exit(1)
    except Exception as e:
        click.secho(f"❌ Update failed: {e}", fg="red")
        sys.exit(1)

@main.command("auto-update")
@click.option("--enable", is_flag=True, help="Enable cron-based auto-update")
@click.option("--disable", is_flag=True, help="Disable cron-based auto-update")
@click.option(
    "--time",
    default="* 5 * * *",
    help="Cron schedule (cron syntax), e.g. '* * * * *' for every minute"
)
def auto_update(enable, disable, time):
    """Manage automatic updates."""
    if enable:
        enable_auto_update(time)
        click.secho("✅ Auto-update enabled (with notifications).", fg="green")
    elif disable:
        disable_auto_update()
        click.secho("✅ Auto-update disabled.", fg="green")
    else:
        click.secho("Use --enable or --disable.", fg="yellow")
        sys.exit(1)

if __name__ == "__main__":
    main()