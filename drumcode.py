#!/usr/bin/env python3

import argparse
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://www.youtube.com/feeds/videos.xml?playlist_id="

PLAYLISTS = {
    "Drumcode Radio": "PLhkZrfli9PCoqrzwkAg2RMAHKzEeVzM2X",
    "Drumcode Streams": "PLhkZrfli9PCrVtlDxynDixY2frHBq_MYW",
    "Adam Beyer Live": "PLhkZrfli9PCqFDIT3_jSAsOVYRhfrVNXF",
}

NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_latest_entry(name, playlist_id):
    url = FEED_URL + playlist_id
    try:
        with urllib.request.urlopen(url) as response:
            feed_xml = response.read()
    except urllib.error.URLError as e:
        print(f"Failed to fetch {name}: {e}", file=sys.stderr)
        return None

    root = ET.fromstring(feed_xml)
    entry = root.find("atom:entry", NS)
    if entry is None:
        return None

    title = entry.findtext("atom:title", default="Unknown", namespaces=NS)
    published = entry.findtext("atom:published", default="", namespaces=NS)
    link = entry.find("atom:link", NS)
    video_url = link.get("href") if link is not None else None

    if not video_url:
        return None

    return {"title": title, "published": published, "url": video_url, "playlist": name}


def pick_entry(entries):
    """Interactive picker using arrow keys and enter."""
    import tty
    import termios
    import shutil

    selected = 0
    count = len(entries)
    cols = shutil.get_terminal_size().columns

    def render():
        # Move cursor up to overwrite previous render (except first time)
        sys.stdout.write(f"\033[{count}A" if render.drawn else "")
        for i, entry in enumerate(entries):
            prefix = "▸ " if i == selected else "  "
            highlight = "\033[1;36m" if i == selected else "\033[0m"
            line = f"{prefix}[{entry['playlist']}] {entry['title']}"
            if len(line) > cols:
                line = line[: cols - 1] + "…"
            sys.stdout.write(f"\033[2K{highlight}{line}\033[0m\r\n")
        sys.stdout.flush()
        render.drawn = True

    render.drawn = False

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        render()
        while True:
            ch = sys.stdin.read(1)
            if ch == "\r" or ch == "\n":
                break
            if ch == "\x03":  # Ctrl-C
                raise KeyboardInterrupt
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":  # Up
                    selected = (selected - 1) % count
                elif seq == "[B":  # Down
                    selected = (selected + 1) % count
                render()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return entries[selected]


def main():
    parser = argparse.ArgumentParser(description="Play the latest Drumcode video")
    parser.add_argument("--info", action="store_true", help="show the latest video info without playing")
    parser.add_argument("--pick", action="store_true", help="pick from the 3 latest sets interactively")
    parser.add_argument("--fullsize", action="store_true", help="play at original resolution instead of 384p height")
    args = parser.parse_args()

    entries = []
    for name, playlist_id in PLAYLISTS.items():
        entry = fetch_latest_entry(name, playlist_id)
        if entry:
            entries.append(entry)

    if not entries:
        print("No videos found in any playlist.", file=sys.stderr)
        sys.exit(1)

    entries.sort(key=lambda e: e["published"], reverse=True)

    if args.pick:
        top = entries[:3]
        print("Pick a set:")
        chosen = pick_entry(top)
    else:
        chosen = entries[0]

    if args.info:
        print(f"[{chosen['playlist']}] {chosen['title']}")
        print(f"Published: {chosen['published']}")
        print(f"URL: {chosen['url']}")
        return

    print(f"[{chosen['playlist']}] Playing: {chosen['title']}")
    cmd = ["mpv"]
    if not args.fullsize:
        cmd.append("--autofit=x384")
    cmd.append(chosen["url"])
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
