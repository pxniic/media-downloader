#!/usr/bin/env python3
"""
downloader.py — Downloader com menu interativo pra YouTube, Twitter/X e Instagram.
"""

import sys
import os
import json
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("✘ Erro: yt-dlp não encontrado. Rode o setup.ps1 ou: pip install yt-dlp")
    input("\nPressione Enter para sair...")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent if "__file__" in globals() else Path(".")
CONFIG_FILE = SCRIPT_DIR / "config.json"
COOKIES_FILE = SCRIPT_DIR / "cookies.txt"


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
    print("║           DOWNLOADER — VÍDEOS / ÁUDIOS          ║")
    print("║        YouTube · Twitter/X · Instagram          ║")
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
    print(f"  {C.GREEN}3{C.RESET} - Só áudio (mp3)")
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
    outtmpl = os.path.join(output_dir, "%(extractor)s - %(title).80s.%(ext)s")

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
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    if choice == "4":
        opts["postprocessors"] = opts.get("postprocessors", []) + [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "gif",
        }]

    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)

    return opts


def baixar(output_dir, url, choice, quality=None):
    opts = build_opts(output_dir, choice, quality)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        print(f"\n{C.GREEN}{C.BOLD}🎉 Download concluído! Salvo em: {output_dir}{C.RESET}\n")
    except yt_dlp.utils.DownloadError as e:
        print(f"\n{C.RED}✘ Erro ao baixar: {e}{C.RESET}\n")
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}✘ Cancelado.{C.RESET}\n")


def main():
    _enable_ansi_windows()
    banner()

    config = load_config()
    if config is None:
        config = setup_wizard()
    output_dir = config["output_dir"]

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
