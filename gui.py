#!/usr/bin/env python3
"""Serve a interface HTML local e dispara os downloads."""

import json
import mimetypes
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from downloader import (
    RESOURCE_DIR,
    baixar,
    default_music_dir,
    load_config,
    resolve_output_dir,
    save_config,
)

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
WEB_DIR = RESOURCE_DIR / "web"
ALLOWED_HOSTS = (
    "youtube.com",
    "youtu.be",
    "music.youtube.com",
    "x.com",
    "twitter.com",
    "instagram.com",
)
CHOICES = {"video": "1", "mp3": "3", "gif": "4"}
MEDIA_EXTS = {".mp3", ".m4a", ".opus", ".ogg", ".wav", ".flac", ".mp4", ".webm", ".mkv", ".gif"}
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def _host_allowed(url: str) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    return any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def _read_clipboard():
    commands = (
        ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
        ["wl-paste", "-n"],
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "--clipboard", "--output"],
    )
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
        text = (result.stdout or "").strip()
        if result.returncode == 0 and text:
            return text
    return ""


def _split_filename(stem):
    if " - " in stem:
        left, right = stem.split(" - ", 1)
        return right.strip(), left.strip()
    return stem.strip(), ""


def _list_library():
    folder = Path(_output_dir())
    items = []
    if not folder.is_dir():
        return items
    for path in folder.iterdir():
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in MEDIA_EXTS:
            continue
        title, artist = _split_filename(path.stem)
        mtime = path.stat().st_mtime
        items.append({
            "title": title or path.stem,
            "artist": artist,
            "name": path.name,
            "ext": path.suffix.lower().lstrip("."),
            "downloaded_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            "downloaded_ts": int(mtime),
        })
    items.sort(key=lambda item: item["downloaded_ts"], reverse=True)
    return items


def _cover_type(data: bytes):
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[:16]:
        return "image/webp"
    return "image/jpeg"


def _extract_cover(media: Path):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        sidecar = media.with_suffix(ext)
        if sidecar.is_file():
            data = sidecar.read_bytes()
            if data:
                return data, _cover_type(data)
    commands = (
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-i", str(media), "-an", "-vcodec", "copy",
            "-f", "image2pipe", "-vframes", "1", "pipe:1",
        ],
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-i", str(media), "-map", "0:v:0", "-frames:v", "1",
            "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1",
        ],
    )
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, timeout=8, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
        if result.returncode == 0 and result.stdout:
            return result.stdout, _cover_type(result.stdout)
    return None, None


def _media_file(name: str):
    if not name:
        return None
    folder = Path(_output_dir()).resolve()
    target = (folder / Path(unquote(name)).name).resolve()
    try:
        target.relative_to(folder)
    except ValueError:
        return None
    if not target.is_file() or target.suffix.lower() not in MEDIA_EXTS:
        return None
    return target


_output_dir_override = None


def _in_container() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def _volume_dir() -> str:
    return (os.environ.get("OUTPUT_DIR") or "").strip()


def _volume_host_path() -> str:
    targets = {"/downloads", _volume_dir()}
    try:
        for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) >= 5 and fields[4] in targets:
                return fields[3]
    except OSError:
        pass
    return ""


def _host_home() -> str:
    env = (os.environ.get("HOST_HOME") or "").strip()
    if env:
        return env
    host_music = _volume_host_path()
    if host_music:
        return str(Path(host_music).parent)
    return ""


def _chosen_dir() -> str:
    if _output_dir_override:
        return _output_dir_override
    config = load_config() or {}
    return str(config.get("output_dir") or "").strip()


def _path_aliases(*values):
    aliases = set()
    for raw in values:
        if not raw:
            continue
        text = str(raw).strip().rstrip("/\\")
        aliases.add(text)
        expanded = Path(text).expanduser()
        aliases.add(str(expanded))
        try:
            aliases.add(str(expanded.resolve()))
        except OSError:
            pass
    return aliases


def _user_music_aliases():
    homes = [str(Path.home())]
    host = _host_home()
    if host:
        homes.append(host)
    values = [
        _volume_dir(),
        _volume_host_path(),
        "/downloads",
        "~/Músicas",
        "~/Music",
        default_music_dir(),
    ]
    if host:
        values.append(default_music_dir(host))
    for home in homes:
        values.extend((str(Path(home) / "Músicas"), str(Path(home) / "Music")))
    return _path_aliases(*values)


def _is_user_music_path(raw: str) -> bool:
    if not str(raw or "").strip():
        return True
    return bool(_path_aliases(raw) & _user_music_aliases())


def _output_dir() -> str:
    chosen = _chosen_dir()
    if _is_user_music_path(chosen):
        volume = _volume_dir()
        if volume:
            return resolve_output_dir(volume)
        return resolve_output_dir(default_music_dir())
    if _in_container() and _volume_dir():
        return resolve_output_dir(_volume_dir())
    return resolve_output_dir(chosen)


def _display_dir() -> str:
    chosen = _chosen_dir()
    if chosen and not _is_user_music_path(chosen) and not _in_container():
        return str(Path(chosen).expanduser())
    host_music = _volume_host_path()
    if host_music:
        return host_music
    host = _host_home()
    if host:
        return default_music_dir(host)
    return default_music_dir()


def _set_output_dir(raw: str) -> str:
    global _output_dir_override
    path = str(raw or "").strip().strip('"')
    if not path:
        raise ValueError("Digite um caminho válido.")
    if _in_container() and not _is_user_music_path(path):
        raise ValueError("No Linux, o padrão é a pasta Músicas do usuário.")
    try:
        resolved = _output_dir() if _is_user_music_path(path) else resolve_output_dir(path)
    except OSError:
        raise ValueError("Não consegui criar essa pasta.")
    if not Path(resolved).is_dir():
        raise ValueError("Essa pasta não existe.")
    stored = default_music_dir(_host_home() or None) if _is_user_music_path(path) else path
    config = load_config() or {}
    config["output_dir"] = stored
    save_config(config)
    _output_dir_override = stored
    return _display_dir()


def _pick_folder_windows(initial: str) -> str | None:
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$d.Description = 'Pasta de download'; "
        "$d.ShowNewFolderButton = $true; "
        "if ($env:MD_INITIAL_DIR -and (Test-Path -LiteralPath $env:MD_INITIAL_DIR)) { "
        "$d.SelectedPath = $env:MD_INITIAL_DIR }; "
        "if ($d.ShowDialog() -eq 'OK') { "
        "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false; "
        "[Console]::Write($d.SelectedPath) }"
    )
    env = os.environ.copy()
    env["MD_INITIAL_DIR"] = initial
    result = subprocess.run(
        ["powershell", "-STA", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
        env=env,
    )
    path = (result.stdout or "").strip()
    return path or None


def _pick_folder_linux(initial: str) -> str | None:
    commands = (
        ["zenity", "--file-selection", "--directory", f"--filename={initial}/", "--title=Pasta de download"],
        ["kdialog", "--getexistingdirectory", initial, "Pasta de download"],
    )
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
        if result.returncode == 0:
            path = (result.stdout or "").strip()
            if path:
                return path
            return None
        if result.returncode == 1:
            return None
    if getattr(sys, "frozen", False):
        return ""
    code = (
        "import sys\n"
        "from tkinter import Tk, filedialog\n"
        "root = Tk(); root.withdraw(); root.attributes('-topmost', True)\n"
        "path = filedialog.askdirectory(initialdir=sys.argv[1] or None, title='Pasta de download')\n"
        "print(path or '', end='')\n"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, initial],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""
    if result.returncode != 0:
        return ""
    path = (result.stdout or "").strip()
    return path or None


def _can_pick_folder() -> bool:
    return not _in_container()


def _pick_folder() -> str | None:
    initial = _display_dir()
    try:
        if os.name == "nt":
            return _pick_folder_windows(initial)
        return _pick_folder_linux(initial)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, code, body, content_type="text/html; charset=utf-8"):
        payload = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Permissions-Policy", "clipboard-read=(self), clipboard-write=(self)")
        self.end_headers()
        self.wfile.write(payload)

    def _send_media(self, path: Path):
        size = path.stat().st_size
        start, end = 0, size - 1
        code = 200
        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes=") and size:
            spec = range_header.split("=", 1)[1]
            left, _, right = spec.partition("-")
            try:
                if left:
                    start = int(left)
                if right:
                    end = int(right)
            except ValueError:
                start, end = 0, size - 1
            start = max(0, min(start, size - 1))
            end = max(start, min(end, size - 1))
            code = 206
        length = end - start + 1
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        with path.open("rb") as handle:
            handle.seek(start)
            remaining = length
            while remaining:
                chunk = handle.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/file":
            name = parse_qs(parsed.query).get("name", [""])[0]
            media = _media_file(name)
            if media is None:
                self._send(404, "Not found")
                return
            self._send_media(media)
            return
        if path == "/cover":
            name = parse_qs(parsed.query).get("name", [""])[0]
            media = _media_file(name)
            if media is None:
                self._send(404, "Not found")
                return
            cover, content_type = _extract_cover(media)
            if not cover:
                self._send(404, "Not found")
                return
            self._send(200, cover, content_type)
            return
        if path == "/clipboard":
            text = _read_clipboard()
            self._send(200, json.dumps({"text": text}), "application/json")
            return
        if path == "/library":
            self._send(200, json.dumps({"items": _list_library()}), "application/json")
            return
        if path == "/settings":
            self._send(200, json.dumps({
                "output_dir": _display_dir(),
                "can_pick": _can_pick_folder(),
            }), "application/json")
            return
        if path == "/":
            path = "/index.html"
        target = (WEB_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(WEB_DIR.resolve())) or not target.is_file():
            self._send(404, "Not found")
            return
        content_type = MIME.get(target.suffix, mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self._send(200, target.read_bytes(), content_type)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/settings":
            try:
                data = self._read_json()
                output_dir = _set_output_dir(data.get("output_dir", ""))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send(400, json.dumps({"ok": False, "message": "Pedido inválido."}), "application/json")
                return
            except ValueError as exc:
                self._send(400, json.dumps({"ok": False, "message": str(exc)}), "application/json")
                return
            self._send(200, json.dumps({"ok": True, "output_dir": output_dir}), "application/json")
            return
        if path == "/pick-folder":
            if not _can_pick_folder():
                self._send(200, json.dumps({
                    "ok": False,
                    "manual": True,
                    "output_dir": _display_dir(),
                }), "application/json")
                return
            picked = _pick_folder()
            if picked:
                try:
                    output_dir = _set_output_dir(picked)
                except ValueError as exc:
                    self._send(400, json.dumps({"ok": False, "message": str(exc)}), "application/json")
                    return
                self._send(200, json.dumps({"ok": True, "output_dir": output_dir}), "application/json")
                return
            if picked is None:
                self._send(200, json.dumps({"ok": False, "cancelled": True}), "application/json")
                return
            self._send(200, json.dumps({
                "ok": False,
                "manual": True,
                "output_dir": _display_dir(),
            }), "application/json")
            return
        if path != "/download":
            self._send(404, json.dumps({"ok": False, "message": "Not found"}), "application/json")
            return
        try:
            data = self._read_json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(400, json.dumps({"ok": False, "message": "Pedido inválido."}), "application/json")
            return

        url = str(data.get("url", "")).strip()
        choice = CHOICES.get(str(data.get("fmt", "mp3")), "3")
        if not _host_allowed(url):
            body = json.dumps({
                "ok": False,
                "message": "Cole um link do YouTube, X/Twitter ou Instagram.",
            })
            self._send(400, body, "application/json")
            return

        ok, result = baixar(_output_dir(), url, choice)
        if ok:
            payload = {"ok": True, **result}
        else:
            payload = {"ok": False, "message": result}
        self._send(200 if ok else 500, json.dumps(payload), "application/json")


def main():
    url = f"http://127.0.0.1:{PORT}/"
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        if os.environ.get("NO_BROWSER") != "1":
            webbrowser.open(url)
        return
    print(f"Interface em {url}")
    print("Deixe este processo rodando. Ctrl+C para sair.")
    if os.environ.get("NO_BROWSER") != "1":
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nFechado.")
        server.shutdown()


if __name__ == "__main__":
    main()
