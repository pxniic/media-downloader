<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Python][python-shield]][python-url]
[![License][license-shield]][license-url]
[![Platform][platform-shield]][platform-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Media Downloader</h3>

  <p align="center">
    Baixe vídeo, áudio e GIF do YouTube, Twitter/X e Instagram direto pro seu PC, sem depender de sites online.
    <br />
    Interface web local em <code>http://127.0.0.1:8765/</code> — no Linux e no Windows.
    <br />
    <a href="#usage"><strong>Ver como usar »</strong></a>
    <br />
    <br />
    <a href="https://github.com/pxniic/media-downloader/issues/new?labels=bug">Reportar Bug</a>
    ·
    <a href="https://github.com/pxniic/media-downloader/issues/new?labels=enhancement">Sugerir Funcionalidade</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Sumário</summary>
  <ol>
    <li>
      <a href="#about-the-project">Sobre o Projeto</a>
      <ul>
        <li><a href="#built-with">Construído com</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Como Começar</a>
      <ul>
        <li><a href="#prerequisites">Pré-requisitos</a></li>
        <li><a href="#linux">Linux</a></li>
        <li><a href="#windows">Windows (.exe)</a></li>
      </ul>
    </li>
    <li><a href="#usage">Uso</a></li>
    <li><a href="#twitter-authentication">Autenticação para Twitter/X</a></li>
    <li><a href="#troubleshooting">Problemas Comuns</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contribuindo</a></li>
    <li><a href="#license">Licença</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## Sobre o Projeto
<a id="about-the-project"></a>

Media Downloader baixa vídeo, áudio (MP3 320 kbps) e GIF do YouTube, Twitter/X e Instagram, sem sites intermediários. A interface principal é uma página local no navegador. O menu em terminal (`python downloader.py`) continua disponível.

Dois jeitos de usar:

- **Linux:** `python3 gui.py` ou container (Podman/Docker) em `http://127.0.0.1:8765/`
- **Windows:** `MediaDownloader.exe` (PyInstaller), atalho no Menu Iniciar e início no login

Principais funcionalidades:

- Interface web com download (MP3 padrão) e playlist/player
- Vídeo (melhor qualidade ou escolhida), áudio MP3 e GIF
- Pasta padrão: Músicas do usuário no Linux, Music/Músicas no Windows (menu ⋮ para trocar)
- Card **Adicionada** após o download (abre a playlist ou dá play)
- Autenticação opcional via cookies para o Twitter/X
- Capa embutida no MP3 (downloads novos) e controle de mídia do sistema (Media Session)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

### Construído com
<a id="built-with"></a>

* [![Python][python-badge]][python-url]
* [yt-dlp](https://github.com/yt-dlp/yt-dlp): extração e download de mídia
* [ffmpeg](https://ffmpeg.org): conversão e merge de áudio/vídeo
* [Deno](https://deno.com): runtime JS exigido pelo yt-dlp para extração do YouTube

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- GETTING STARTED -->
## Como Começar
<a id="getting-started"></a>

### Pré-requisitos
<a id="prerequisites"></a>

- [Python 3.10+](https://python.org/downloads)
- [ffmpeg](https://ffmpeg.org)
- [Deno](https://deno.com/install)

No Windows o instalador instala isso via `winget`. No Linux, use o gerenciador da distro.

---

## Linux
<a id="linux"></a>

### Dependências

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg
# Deno: https://deno.com/install
curl -fsSL https://deno.land/install.sh | sh
```

### Projeto e pacotes

```bash
cd media-downloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se o sistema bloquear `pip` (PEP 668), use o `venv` — não instale no Python do sistema.

### Configuração

A pasta padrão é a de músicas do usuário atual:

- Linux: `~/Músicas` (ou o caminho do `xdg-user-dir MUSIC`)
- Windows: pasta Music/Músicas da conta

Para trocar: na interface, três pontos no canto do card → **Pasta de download**. A escolha fica em `config.json` (não versionado). `~` é expandido automaticamente.

No container, `~/Músicas` do host é montada em `/downloads`. A interface mostra o caminho do host; os arquivos saem nessa pasta.

### Rodar a interface web

```bash
source .venv/bin/activate
python3 gui.py
```

Abre [http://127.0.0.1:8765/](http://127.0.0.1:8765/). Deixe o terminal aberto. MP3 já vem selecionado.

### Menu no terminal

```bash
python3 downloader.py
```

### Container (opcional, sobe no boot)

Requer Podman ou Docker. A imagem inclui Python, `yt-dlp`, ffmpeg e Deno.

```bash
podman build -t localhost/media-downloader:local .
mkdir -p "$HOME/Músicas"
```

**Compose:**

```bash
docker compose up -d --build
```

`~/Músicas` no host é montada em `/downloads` no container.

**Início automático (Podman Quadlet + systemd do usuário):**

```bash
mkdir -p ~/.config/containers/systemd
cp deploy/media-downloader.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start media-downloader.service
loginctl enable-linger "$USER"
```

```bash
systemctl --user status media-downloader.service
systemctl --user restart media-downloader.service
```

Depois de mudar o código:

```bash
podman build -t localhost/media-downloader:local .
systemctl --user restart media-downloader.service
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

## Windows (.exe)
<a id="windows"></a>

O `.exe` **precisa ser gerado no Windows**. Não dá para cross-compilar a partir do Linux.

Python entra só na hora do build. No uso diário você abre o `MediaDownloader.exe`. ffmpeg e Deno continuam no sistema.

### Pré-requisitos no PC Windows

- Windows 10/11
- [App Installer](https://apps.microsoft.com/detail/9nblggh4nns1) (traz o `winget`)
- Clone ou copie este repositório

Se a política de scripts bloquear o PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Só gerar o exe

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\build.ps1
```

O script instala PyInstaller e empacota `gui.py`, `downloader.py`, `web/` e `yt-dlp`.

Arquivo gerado:

```
dist\MediaDownloader\MediaDownloader.exe
```

### Instalar (exe + atalho + início no login)

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
```

Ou dê dois cliques em `setup.bat`.

O instalador:

1. Instala Python 3.12, ffmpeg e Deno com `winget` (se faltar)
2. Roda `windows\build.ps1`
3. Copia o exe para `%LOCALAPPDATA%\MediaDownloader`
4. Cria o atalho **Media Downloader** no Menu Iniciar
5. Registra início automático no login
6. Abre [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

Pasta padrão das músicas: `%USERPROFILE%\Music` (`config.json` em `%LOCALAPPDATA%\MediaDownloader`).

### Desinstalar

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\MediaDownloader\uninstall.ps1"
```

Remove o app, o atalho e o início automático. Python, ffmpeg e Deno do sistema ficam.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- USAGE EXAMPLES -->
## Uso
<a id="usage"></a>

Abra [http://127.0.0.1:8765/](http://127.0.0.1:8765/) (via `gui.py` no Linux ou o exe no Windows).

- Aba **Download:** cole o link e baixe (MP3, vídeo ou GIF)
- Aba **Playlist:** lista as faixas (mais recentes primeiro) e o player
- Menu ⋮: pasta de download
- Card **Adicionada** (10 s): clique abre a Playlist; o play inicia a faixa

O menu no terminal:

```bash
python3 downloader.py
```

```
1 - Vídeo (melhor qualidade)
2 - Vídeo (escolher qualidade)
3 - Só áudio (mp3)
4 - GIF
0 - Sair
```

Para trocar a pasta de destino, use o menu ⋮ da interface (ou edite o `config.json`).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- TWITTER AUTH -->
## Autenticação para Twitter/X
<a id="twitter-authentication"></a>

O Twitter/X às vezes retorna “vídeo não encontrado” mesmo em post público. Para resolver:

1. Instale uma extensão tipo **Get cookies.txt LOCALLY**
2. Faça login no x.com
3. Exporte os cookies do domínio
4. Renomeie para `cookies.txt`
5. Coloque o arquivo:
   - **Linux (Python):** ao lado de `downloader.py`
   - **Linux (container):** monte em `/app/cookies.txt` ou copie para o projeto antes do build
   - **Windows (exe):** em `%LOCALAPPDATA%\MediaDownloader\cookies.txt`

> **Atenção:** `cookies.txt` contém um token de sessão ativo. Não faça commit nem compartilhe. O `.gitignore` já exclui esse arquivo e o `config.json`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- TROUBLESHOOTING -->
## Problemas Comuns
<a id="troubleshooting"></a>

| Problema | Solução |
|---|---|
| Erro `HTTP 403` no YouTube | Confirme o Deno: `deno --version` |
| `yt-dlp` não encontrado | `pip install -U yt-dlp` (ou regenere o exe) |
| MP3/GIF falha no pós-processamento | Instale ffmpeg e deixe no PATH |
| Vídeo do Twitter/X não encontrado | Configure `cookies.txt` |
| Colar bloqueado no navegador | Ícone de colar ou Ctrl+V |
| Porta 8765 em uso | O app tenta abrir a interface que já está rodando |
| `setup.bat` bloqueado | Rode `.\setup.bat` no PowerShell, ou `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `Requested format is not available` | Atualize o yt-dlp: `pip install -U yt-dlp` |
| Exe não gera no Linux | O build do `.exe` só funciona no Windows |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- ROADMAP -->
## Roadmap
<a id="roadmap"></a>

- [x] Menu interativo
- [x] Interface web local
- [x] Playlist e player
- [x] Empacotamento em `.exe` (PyInstaller)
- [x] Suporte a cookies para Twitter/X
- [x] Fallback automático de formato
- [ ] Suporte a corte de vídeo (via ffmpeg) integrado ao menu
- [ ] Empacotamento em `.exe` assinado

Veja as [issues abertas](https://github.com/pxniic/media-downloader/issues) para a lista completa.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Estrutura

```
media-downloader/
├── downloader.py              # Download + menu no terminal
├── gui.py                     # Servidor da interface web
├── web/                       # HTML, CSS e JS
├── requirements.txt           # yt-dlp
├── MediaDownloader.spec       # PyInstaller (Windows)
├── Dockerfile                 # Imagem Linux
├── compose.yaml
├── .dockerignore
├── deploy/media-downloader.container
├── windows/
│   ├── build.ps1              # Gera o .exe
│   ├── install.ps1            # Build + instala + inicia no login
│   └── uninstall.ps1
├── setup.bat                  # Atalho para install.ps1
├── LICENSE
└── README.md
```

<!-- CONTRIBUTING -->
## Contribuindo
<a id="contributing"></a>

Contribuições são bem-vindas.

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/MinhaFeature`)
3. Faça o Commit das mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Faça o Push para a Branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- LICENSE -->
## Licença
<a id="license"></a>

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[python-shield]: https://img.shields.io/badge/python-3.10%2B-blue
[python-badge]: https://img.shields.io/badge/python-3.10%2B-blue
[python-url]: https://python.org
[license-shield]: https://img.shields.io/badge/license-MIT-green
[license-url]: https://github.com/pxniic/media-downloader/blob/main/LICENSE
[platform-shield]: https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey
[platform-url]: https://github.com/pxniic/media-downloader
