# MediaDownloader

Media downloader application using yt-dlp, providing a graphic interface for ease of use for more common users.

## Credits

Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [FFmpeg](https://www.ffmpeg.org/)..

## Installation

### Windows PowerShell

To install the app as .exe(AppData\Local)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/alpineplacebo/MediaDownloader-yt-dlp/master/install.ps1'))
```

### Running from Source

You can install dependencies using `uv` or `pip`.
To run:
- Python 3.10 or higher
- [ffmpeg](https://ffmpeg.org/download.html) (required for media processing)

#### Using uv

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies and run
uv sync
uv run main.py
```

#### The classic way (using pip)

```bash
pip install -r requirements.txt
# or directly from pyproject.toml if you don't have a requirements.txt generated
pip install .

python main.py
```

### Building the Executable

To build a standalone executable:
Download [ffmpeg](https://ffmpeg.org/download.html) and drop in bin/, so it has bin/ffmpeg.exe and bin/ffprobe.exe
```bash
uv run pyinstaller MediaDownloader.spec
```

