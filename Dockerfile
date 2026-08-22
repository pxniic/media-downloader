FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl unzip wl-clipboard xclip \
    && rm -rf /var/lib/apt/lists/*

ENV DENO_INSTALL=/usr/local
RUN curl -fsSL https://deno.land/install.sh | sh \
    && ln -sf /usr/local/bin/deno /usr/bin/deno

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY downloader.py gui.py ./
COPY web ./web

ENV HOST=0.0.0.0
ENV PORT=8765
ENV OUTPUT_DIR=/downloads
ENV NO_BROWSER=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8765
RUN mkdir -p /downloads

CMD ["python", "-u", "gui.py"]
