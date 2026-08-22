# Media Downloader

A command-line tool for downloading video, audio, and GIF content from YouTube, Twitter/X, and Instagram. Runs locally on Windows with no dependency on external web services.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## Features

- Downloads video, audio-only (MP3), and GIF content
- Supports YouTube, Twitter/X, and Instagram URLs
- Interactive menu interface with progress display
- Configurable output directory, set once on first run
- Optional cookie-based authentication for restricted content
- Built on `yt-dlp` and `ffmpeg` for format extraction and conversion

## Requirements

- Windows 10/11
- Python 3.10 or later
- ffmpeg
- Deno (required by `yt-dlp` for YouTube's JavaScript-based signature verification)

## 📦 Installation

### Automated setup

1. Clone or download this repository.
2. Right-click `setup.ps1` and select **Run with PowerShell**.
   If script execution is blocked, run the following in PowerShell first:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\setup.ps1
   ```
3. The script installs Python, ffmpeg, Deno, and `yt-dlp` via `winget` and `pip`.
4. If any dependency was installed for the first time, close and reopen the terminal before proceeding.

### Manual setup

```powershell
# Install Python 3.10+ from python.org, ensuring "Add python.exe to PATH" is checked

# Install ffmpeg and add it to PATH
# https://ffmpeg.org

# Install Deno
# https://deno.com/install

# Install Python dependencies
pip install -r requirements.txt
```

## 🚀 Usage

Run the script from the project directory:

```powershell
python downloader.py
```

On first run, the program prompts for an output directory and stores it in `config.json`. Subsequent runs use this value automatically.

The main menu presents the following options:

```
1 - Video (best available quality)
2 - Video (select quality)
3 - Audio only (MP3)
4 - GIF
0 - Exit
```

Paste a URL when prompted and press Enter. After each download completes, the program asks whether to process another URL.

To change the output directory later, delete `config.json` and run the program again, or edit the file directly.

## Authentication for Twitter/X

Twitter/X occasionally returns a "no video found" error for unauthenticated requests, even on public content. To resolve this:

1. Install a cookie export extension, such as **Get cookies.txt LOCALLY**, in your browser.
2. Log in to x.com.
3. With the X tab active, use the extension to export cookies for the domain.
4. Rename the exported file to `cookies.txt`.
5. Place `cookies.txt` in the same directory as `downloader.py`.

The program detects this file automatically and applies it to subsequent requests.

**Note:** `cookies.txt` contains an active session token for the account used to export it. Do not commit this file to version control or share it. The included `.gitignore` excludes it by default.

## Troubleshooting

| Issue | Resolution |
|---|---|
| `HTTP 403` error on YouTube downloads | Confirm Deno is installed: `deno --version` |
| `yt-dlp` not found | Run `pip install -U yt-dlp` |
| Twitter/X video not found | Configure cookie authentication (see above) |
| `setup.ps1` fails to execute | PowerShell execution policy is restricting scripts; see the bypass command under Installation |

## Project structure

```
media-downloader/
├── downloader.py       # Main application
├── setup.ps1           # Automated dependency installer
├── requirements.txt    # Python dependencies
├── .gitignore           # Excludes cookies.txt and config.json from version control
└── README.md
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/description`).
3. Commit your changes with a clear message.
4. Open a pull request describing the change and its motivation.

Please avoid introducing new external dependencies without discussion, and keep the CLI interface consistent with the existing menu structure.

## License

MIT
