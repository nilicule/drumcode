# drumcode

CLI tool that fetches the latest video from Drumcode's YouTube playlists and plays it with [mpv](https://mpv.io/).

Tracks these playlists:
- Drumcode Radio
- Drumcode Streams
- Adam Beyer Live

## Requirements

- Python 3
- [mpv](https://mpv.io/)

## Usage

```sh
python drumcode.py
```

The script picks the most recently published video across all playlists and opens it in mpv at a 384px window height.

### Options

- `--info` - Show the latest video title, date, and URL without playing
- `--pick` - Interactively pick from the latest video of each playlist using arrow keys
- `--fullsize` - Play at original resolution instead of the default 384p height
