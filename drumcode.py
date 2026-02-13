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


def main():
    parser = argparse.ArgumentParser(description="Play the latest Drumcode video")
    parser.add_argument("--info", action="store_true", help="show the latest video info without playing")
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

    latest = max(entries, key=lambda e: e["published"])

    if args.info:
        print(f"[{latest['playlist']}] {latest['title']}")
        print(f"Published: {latest['published']}")
        print(f"URL: {latest['url']}")
        return

    print(f"[{latest['playlist']}] Playing: {latest['title']}")
    cmd = ["mpv"]
    if not args.fullsize:
        cmd.append("--autofit=x384")
    cmd.append(latest["url"])
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
