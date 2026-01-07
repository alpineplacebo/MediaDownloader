# MediaDownloader

A simple and efficient media downloader application, more common user-friendly bundle for yt-dlp.

## Credits

Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Installation

### Prerequisites

- Python 3.10 or higher
- [ffmpeg](https://ffmpeg.org/download.html) (required for media processing)

### Running from Source

You can install dependencies using `uv` or `pip`.

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

```bash
uv run pyinstaller MediaDownloader.spec
```

### One-Line Install (PowerShell)

To install, you must have the **[GitHub CLI (gh)](https://cli.github.com/)** installed and authenticated.

Run this command in PowerShell:

```powershell
gh api -H "Accept: application/vnd.github.v3.raw" /repos/alpineplacebo/MediaDownloader/contents/install.ps1 | iex
```

> **Note**: Since this is a private repository, `gh` handles the authentication required to download the script and the application.
