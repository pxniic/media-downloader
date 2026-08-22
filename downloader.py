#!/usr/bin/env python3
"""
downloader.py — Downloader com menu interativo pra YouTube, Twitter/X e Instagram.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

try:
    import yt_dlp
except ImportError:
    print("✘ Erro: yt-dlp não encontrado. Rode o setup.ps1 ou: pip install yt-dlp")
    input("\nPressione Enter para sair...")
    sys.exit(1)

def _app_dirs():
    if getattr(sys, "frozen", False):
        resource = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        data = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MediaDownloader"
        data.mkdir(parents=True, exist_ok=True)
        return resource, data
    root = Path(__file__).resolve().parent
    return root, root


RESOURCE_DIR, DATA_DIR = _app_dirs()
SCRIPT_DIR = DATA_DIR
CONFIG_FILE = DATA_DIR / "config.json"
COOKIES_FILE = DATA_DIR / "cookies.txt"


# ── cores no terminal ────────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"


def _enable_ansi_windows():
    if os.name == "nt":
        os.system("")


def banner():
    print(f"{C.CYAN}{C.BOLD}")
    print("╔════════════════════════════════════════════════╗")
    print("║           DOWNLOADER — VÍDEOS / ÁUDIOS         ║")
    print("║        YouTube · Twitter/X · Instagram         ║")
    print("╚════════════════════════════════════════════════╝")
    print(C.RESET)


# ── configuração (primeira execução pergunta e salva) ──────────────────
def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def resolve_output_dir(raw):
    path = Path(raw).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())


def _windows_music_dir():
    try:
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

        folder = GUID(
            0x4BD8D571,
            0x6D19,
            0x48D3,
            (wintypes.BYTE * 8)(0xBE, 0x97, 0x42, 0x22, 0x20, 0x08, 0x0E, 0x43),
        )
        path_ptr = ctypes.c_wchar_p()
        status = ctypes.windll.shell32.SHGetKnownFolderPath(
            ctypes.byref(folder), 0, None, ctypes.byref(path_ptr)
        )
        if status != 0 or not path_ptr.value:
            return None
        path = path_ptr.value
        ctypes.windll.ole32.CoTaskMemFree(path_ptr)
        return path
    except Exception:
        return None


def _xdg_music_dir():
    try:
        result = subprocess.run(
            ["xdg-user-dir", "MUSIC"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    path = (result.stdout or "").strip()
    return path or None


def default_music_dir(home=None):
    root = Path(home).expanduser() if home else Path.home()
    if os.name == "nt":
        known = _windows_music_dir() if home is None else None
        if known:
            return known
        for name in ("Músicas", "Music"):
            candidate = root / name
            if candidate.is_dir():
                return str(candidate)
        return str(root / "Music")
    if home is None:
        xdg = _xdg_music_dir()
        if xdg:
            return xdg
    for name in ("Músicas", "Music"):
        candidate = root / name
        if candidate.is_dir():
            return str(candidate)
    return str(root / "Músicas")


def setup_wizard():
    print(f"{C.YELLOW}{C.BOLD}Primeira vez rodando — configuração inicial{C.RESET}\n")
    while True:
        pasta = input(
            f"{C.YELLOW}Em qual pasta você quer salvar os downloads? "
            f"(ex: C:\\Users\\SeuNome\\Downloads\\midias): {C.RESET}"
        ).strip().strip('"')
        if pasta:
            break
        print(f"{C.RED}Digite um caminho válido.{C.RESET}")

    config = {"output_dir": pasta}
    save_config(config)
    print(f"\n{C.GREEN}✔ Configuração salva! Isso não será perguntado de novo.{C.RESET}")
    print(f"{C.GRAY}(pra mudar depois, edite o arquivo config.json ou apague-o pra refazer esse setup){C.RESET}\n")
    return config


def menu():
    print(f"{C.BOLD}O que você quer baixar?{C.RESET}")
    print(f"  {C.GREEN}1{C.RESET} - Vídeo (melhor qualidade)")
    print(f"  {C.GREEN}2{C.RESET} - Vídeo (escolher qualidade)")
    print(f"  {C.GREEN}3{C.RESET} - Só áudio (MP3 320 kbps)")
    print(f"  {C.GREEN}4{C.RESET} - GIF")
    print(f"  {C.RED}0{C.RESET} - Sair")
    print()
    return input(f"{C.YELLOW}Escolha uma opção: {C.RESET}").strip()


def progress_hook(d):
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        filename = os.path.basename(d.get("filename", ""))
        sys.stdout.write(
            f"\r{C.CYAN}⬇{C.RESET} {filename[:40]:<40} "
            f"{C.GREEN}{pct:>7}{C.RESET}  {speed:>12}  ETA {eta}   "
        )
        sys.stdout.flush()
    elif d["status"] == "finished":
        print(f"\n{C.GREEN}✔ Processando/baixado:{C.RESET} {os.path.basename(d.get('filename', ''))}")


def build_format_string(choice, quality=None):
    if choice == "3":
        return "bestaudio/best"
    if choice == "4":
        return "bestvideo[ext=mp4][height<=720]/best[ext=mp4]"
    if choice == "2" and quality:
        return f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    return "bestvideo+bestaudio/best"


def build_opts(output_dir, choice, quality=None):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    outtmpl = os.path.join(output_dir, "%(title).80s.%(ext)s")

    opts = {
        "format": build_format_string(choice, quality),
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }

    if choice == "3":
        opts["writethumbnail"] = True
        opts["postprocessors"] = [
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
        ]
        opts["postprocessor_args"] = {
            "FFmpegExtractAudio": ["-ar", "48000"],
        }

    if choice == "4":
        opts["postprocessors"] = opts.get("postprocessors", []) + [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "gif",
        }]

    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)

    return opts


def media_meta(info):
    if not info:
        return {"title": "Faixa", "artist": "", "thumbnail": ""}
    if info.get("_type") == "playlist":
        entries = [item for item in (info.get("entries") or []) if item]
        if entries:
            info = entries[0]
    title = (info.get("track") or info.get("title") or "Faixa").strip()
    artist = info.get("artist") or info.get("album_artist") or info.get("creator")
    if isinstance(artist, list):
        artist = ", ".join(str(part) for part in artist if part)
    if not artist:
        artist = info.get("channel") or info.get("uploader") or ""
    artist = str(artist).strip()
    thumbnail = info.get("thumbnail") or ""
    thumbs = info.get("thumbnails") or []
    if thumbs:
        best = max(thumbs, key=lambda item: (item.get("width") or 0) * (item.get("height") or 0))
        thumbnail = best.get("url") or thumbnail
    return {"title": title, "artist": artist, "thumbnail": thumbnail}


def _unwrap_info(info):
    if info and info.get("_type") == "playlist":
        entries = [item for item in (info.get("entries") or []) if item]
        if entries:
            return entries[0]
    return info


def _audio_path(info, output_dir):
    info = _unwrap_info(info) or {}
    names = []
    for item in info.get("requested_downloads") or []:
        names.extend([item.get("filepath"), item.get("filename")])
    names.extend([info.get("filepath"), info.get("filename"), info.get("_filename")])
    for name in names:
        if not name:
            continue
        path = Path(name)
        if path.suffix.lower() != ".mp3":
            path = path.with_suffix(".mp3")
        if path.is_file():
            return path
    title = (info.get("title") or "")[:80]
    if title:
        matches = sorted(
            Path(output_dir).glob("*.mp3"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        for path in matches:
            if title[:30] in path.stem:
                return path
    return None


def _result_path(info, output_dir, choice):
    info = _unwrap_info(info) or {}
    names = []
    for item in info.get("requested_downloads") or []:
        names.extend([item.get("filepath"), item.get("filename")])
    names.extend([info.get("filepath"), info.get("filename"), info.get("_filename")])
    suffix = { "3": ".mp3", "4": ".gif" }.get(choice)
    for name in names:
        if not name:
            continue
        path = Path(name)
        if suffix:
            path = path.with_suffix(suffix)
        if path.is_file():
            return path
    folder = Path(output_dir)
    if folder.is_dir():
        latest = max(
            (item for item in folder.iterdir() if item.is_file() and not item.name.startswith(".")),
            key=lambda item: item.stat().st_mtime,
            default=None,
        )
        if latest is not None:
            return latest
    return None


def _thumbnail_path(audio_path, info):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = audio_path.with_suffix(ext)
        if candidate.is_file():
            return candidate
    url = media_meta(info).get("thumbnail")
    if not url:
        return None
    dest = audio_path.with_suffix(".jpg")
    try:
        with urlopen(url, timeout=20) as response:
            dest.write_bytes(response.read())
        return dest if dest.is_file() and dest.stat().st_size else None
    except Exception:
        return None


def _embed_cover(audio_path, thumb_path):
    tmp = audio_path.with_name(audio_path.stem + ".cover.tmp.mp3")
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-i", str(audio_path),
            "-i", str(thumb_path),
            "-map", "0:a", "-map", "1:0",
            "-c:a", "copy", "-c:v", "mjpeg",
            "-disposition:v:0", "attached_pic",
            "-id3v2_version", "3",
            str(tmp),
        ],
        check=False,
        capture_output=True,
    )
    if result.returncode == 0 and tmp.is_file():
        tmp.replace(audio_path)
        sidecar = audio_path.with_suffix(".jpg")
        if thumb_path.resolve() != sidecar.resolve():
            sidecar.write_bytes(thumb_path.read_bytes())
        return True
    if tmp.exists():
        tmp.unlink()
    return False


def attach_cover(info, output_dir):
    audio_path = _audio_path(info, output_dir)
    if audio_path is None:
        return False
    thumb_path = _thumbnail_path(audio_path, info)
    if thumb_path is None:
        return False
    return _embed_cover(audio_path, thumb_path)


def baixar(output_dir, url, choice, quality=None):
    opts = build_opts(output_dir, choice, quality)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        if choice == "3":
            attach_cover(info, output_dir)
        meta = media_meta(info)
        downloaded = _audio_path(info, output_dir) if choice == "3" else None
        if downloaded is None:
            downloaded = _result_path(info, output_dir, choice)
        if downloaded is not None:
            meta["name"] = downloaded.name
        print(f"\n{C.GREEN}{C.BOLD}🎉 Download concluído!{C.RESET}\n")
        return True, meta
    except yt_dlp.utils.DownloadError as e:
        print(f"\n{C.RED}✘ Erro ao baixar: {e}{C.RESET}\n")
        return False, str(e)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}✘ Cancelado.{C.RESET}\n")
        return False, "Cancelado."


def main():
    _enable_ansi_windows()
    banner()

    config = load_config()
    if config is None or not config.get("output_dir"):
        config = {"output_dir": default_music_dir()}
        save_config(config)
    output_dir = resolve_output_dir(config["output_dir"])

    if not COOKIES_FILE.exists():
        print(f"{C.GRAY}(dica: se for baixar do Twitter/X, coloque um arquivo 'cookies.txt' "
              f"nesta mesma pasta pra evitar erro de vídeo não encontrado — veja o README){C.RESET}\n")

    while True:
        choice = menu()

        if choice == "0":
            print(f"{C.CYAN}Até mais!{C.RESET}")
            break

        if choice not in {"1", "2", "3", "4"}:
            print(f"{C.RED}Opção inválida.{C.RESET}\n")
            continue

        url = input(f"\n{C.YELLOW}Cole o link aqui: {C.RESET}").strip()
        if not url:
            print(f"{C.RED}Nenhum link informado.{C.RESET}\n")
            continue

        quality = None
        if choice == "2":
            quality = input(f"{C.YELLOW}Altura máxima (ex: 1080, 720, 480): {C.RESET}").strip()
            quality = quality if quality.isdigit() else None

        print()
        baixar(output_dir, url, choice, quality)

        de_novo = input(f"{C.CYAN}Baixar outro? (Enter = sim / 'n' = sair): {C.RESET}").strip().lower()
        print()
        if de_novo == "n":
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"\n✘ Ocorreu um erro no programa: {err}")
        input("\nPressione Enter para fechar...")
