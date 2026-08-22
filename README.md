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
    Baixe vídeo, áudio e GIF do YouTube, Twitter/X e Instagram direto pro seu PC — sem depender de sites online.
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
        <li><a href="#installation">Instalação</a></li>
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

Media Downloader é uma ferramenta de linha de comando com menu interativo pra baixar vídeo, áudio (MP3) e GIF do YouTube, Twitter/X e Instagram, sem precisar de sites intermediários. Roda 100% localmente no Windows.

Principais funcionalidades:
- Menu interativo — sem precisar decorar comandos ou flags
- Suporte a vídeo (melhor qualidade ou escolhida), áudio MP3 e GIF
- Pasta de destino configurável, perguntada apenas uma vez
- Autenticação opcional via cookies pra contornar bloqueios do Twitter/X
- Fallback automático de formato quando o serviço de origem muda a entrega de streams

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

### Construído com
<a id="built-with"></a>

* [![Python][python-badge]][python-url]
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) — extração e download de mídia
* [ffmpeg](https://ffmpeg.org) — conversão e merge de áudio/vídeo
* [Deno](https://deno.com) — runtime JS exigido pelo yt-dlp para extração do YouTube

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- GETTING STARTED -->
## Como Começar
<a id="getting-started"></a>

Siga os passos abaixo para ter uma cópia local rodando.

### Pré-requisitos
<a id="prerequisites"></a>

- Windows 10/11
- [Python 3.10+](https://python.org/downloads) (marque "Add python.exe to PATH" no instalador)
- [ffmpeg](https://ffmpeg.org)
- [Deno](https://deno.com/install)

### Instalação
<a id="installation"></a>

**Opção 1 — Setup automático (recomendado)**

1. Clone o repositório
   ```powershell
   git clone https://github.com/pxniic/media-downloader.git
   ```
2. Abra o PowerShell dentro da pasta do projeto e rode o instalador
   ```powershell
   .\setup.bat
   ```
   O script instala Python, ffmpeg, Deno e `yt-dlp` automaticamente via `winget` e `pip`.
3. Se algo foi instalado agora pela primeira vez, feche e reabra o terminal antes de continuar.

**Opção 2 — Manual**

```powershell
pip install -r requirements.txt
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- USAGE EXAMPLES -->
## Uso
<a id="usage"></a>

Rode o programa a partir da pasta do projeto:

```powershell
python downloader.py
```

Na primeira execução, o programa pergunta em qual pasta salvar os downloads e guarda essa resposta em `config.json` — não pergunta de novo depois disso.

O menu principal apresenta as seguintes opções:

```
1 - Vídeo (melhor qualidade)
2 - Vídeo (escolher qualidade)
3 - Só áudio (mp3)
4 - GIF
0 - Sair
```

Cole o link quando solicitado e aperte Enter. Ao final de cada download, o programa pergunta se você quer processar outro link.

Para trocar a pasta de destino depois, apague o `config.json` e rode o programa de novo, ou edite o arquivo diretamente.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- TWITTER AUTH -->
## Autenticação para Twitter/X
<a id="twitter-authentication"></a>

O Twitter/X às vezes retorna erro de "vídeo não encontrado" para requisições não autenticadas, mesmo em conteúdo público. Para resolver:

1. Instale uma extensão de exportação de cookies, como **Get cookies.txt LOCALLY**, no seu navegador.
2. Faça login no x.com.
3. Com a aba do X ativa, use a extensão para exportar os cookies do domínio.
4. Renomeie o arquivo exportado para `cookies.txt`.
5. Coloque `cookies.txt` na mesma pasta do `downloader.py`.

O programa detecta esse arquivo automaticamente e passa a usá-lo nas próximas requisições.

> **Atenção:** `cookies.txt` contém um token de sessão ativo da conta usada para exportá-lo. Não faça commit desse arquivo nem o compartilhe. O `.gitignore` incluído já exclui esse arquivo por padrão.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- TROUBLESHOOTING -->
## Problemas Comuns
<a id="troubleshooting"></a>

| Problema | Solução |
|---|---|
| Erro `HTTP 403` em downloads do YouTube | Confirme que o Deno está instalado: `deno --version` |
| `yt-dlp` não encontrado | Rode `pip install -U yt-dlp` |
| Vídeo do Twitter/X não encontrado | Configure a autenticação por cookies (seção acima) |
| `setup.bat` bloqueado pelo Controle de Aplicativos Inteligente | Rode `.\setup.bat` de dentro do PowerShell, em vez de dar duplo clique no arquivo |
| `Requested format is not available` | O programa já tenta automaticamente um formato alternativo; se persistir, rode `pip install -U yt-dlp` |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- ROADMAP -->
## Roadmap
<a id="roadmap"></a>

- [x] Menu interativo
- [x] Suporte a cookies para Twitter/X
- [x] Fallback automático de formato
- [ ] Suporte a corte de vídeo (via ffmpeg) integrado ao menu
- [ ] Empacotamento em `.exe` assinado

Veja as [issues abertas](https://github.com/pxniic/media-downloader/issues) para a lista completa de funcionalidades propostas e problemas conhecidos.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- CONTRIBUTING -->
## Contribuindo
<a id="contributing"></a>

Contribuições são o que tornam a comunidade open source um lugar incrível para aprender e criar. Qualquer contribuição é **muito bem-vinda**.

Se você tiver uma sugestão, faça um fork do repositório e abra um pull request. Também pode abrir uma issue com a tag "enhancement".

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
[platform-shield]: https://img.shields.io/badge/platform-Windows-lightgrey
[platform-url]: https://github.com/pxniic/media-downloader
