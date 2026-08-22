const go = document.getElementById("go");
const paste = document.getElementById("paste");
const clear = document.getElementById("clear");
const statusEl = document.getElementById("status");
const manual = document.getElementById("manual");
const toast = document.getElementById("toast");
const toastArt = document.getElementById("toast-art");
const toastTitle = document.getElementById("toast-title");
const toastArtist = document.getElementById("toast-artist");
const toastPlay = document.getElementById("toast-play");
const libraryEl = document.getElementById("library");
const libraryEmpty = document.getElementById("library-empty");
const viewDownload = document.getElementById("view-download");
const viewList = document.getElementById("view-list");
const audio = document.getElementById("audio");
const playBtn = document.getElementById("play");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");
const seek = document.getElementById("seek");
const playerTitle = document.getElementById("player-title");
const playerArtist = document.getElementById("player-artist");
const viewTitle = document.getElementById("view-title");
const shuffleBtn = document.getElementById("shuffle");
const timeElapsed = document.getElementById("time-elapsed");
const timeLeft = document.getElementById("time-left");
const playerArt = document.getElementById("player-art");
const menuBtn = document.getElementById("menu-btn");
const menuPanel = document.getElementById("menu-panel");
const folderOption = document.getElementById("folder-option");
const folderPath = document.getElementById("folder-path");
const folderForm = document.getElementById("folder-form");
const folderInput = document.getElementById("folder-input");
const folderError = document.getElementById("folder-error");

let toastTimer;
let toastTrack = null;
let tracks = [];
let currentIndex = -1;
let currentName = "";
let seeking = false;
let shuffle = false;
let canPickFolder = false;

function setError(message) {
  statusEl.textContent = message || "";
}

function setFolderPath(path) {
  folderPath.textContent = path || "Não definida";
  folderInput.value = path || "";
}

function setFolderError(message) {
  folderError.textContent = message || "";
}

function closeMenu() {
  menuPanel.hidden = true;
  menuBtn.setAttribute("aria-expanded", "false");
  folderForm.hidden = true;
  setFolderError("");
}

function toggleMenu() {
  const open = menuPanel.hidden;
  menuPanel.hidden = !open;
  menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  if (!open) {
    folderForm.hidden = true;
    setFolderError("");
  }
}

function showFolderForm() {
  folderForm.hidden = false;
  folderInput.focus();
  folderInput.select();
}

async function loadSettings() {
  try {
    const res = await fetch("/settings");
    const data = await res.json();
    canPickFolder = Boolean(data.can_pick);
    setFolderPath(data.output_dir || "");
  } catch {
    canPickFolder = false;
    setFolderPath("");
  }
}

async function saveFolder(path) {
  const res = await fetch("/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ output_dir: path }),
  });
  const data = await res.json();
  if (!data.ok) {
    throw new Error(data.message || "Não consegui salvar a pasta.");
  }
  setFolderPath(data.output_dir);
  if (!viewList.classList.contains("is-hidden")) {
    loadLibrary();
  }
}

async function pickFolder() {
  setFolderError("");
  if (!canPickFolder) {
    showFolderForm();
    return;
  }
  try {
    const res = await fetch("/pick-folder", { method: "POST" });
    const data = await res.json();
    if (data.ok) {
      setFolderPath(data.output_dir);
      closeMenu();
      if (!viewList.classList.contains("is-hidden")) {
        loadLibrary();
      }
      return;
    }
    if (data.cancelled) return;
    if (data.output_dir) setFolderPath(data.output_dir);
    showFolderForm();
  } catch {
    showFolderForm();
  }
}

function syncClear() {
  clear.hidden = !manual.value;
}

function formatTime(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const total = Math.floor(seconds);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function updateTimes() {
  const current = audio.currentTime || 0;
  const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
  timeElapsed.textContent = formatTime(current);
  timeLeft.textContent = duration ? `-${formatTime(duration - current)}` : "-0:00";
  if (!seeking && duration) {
    seek.value = String((current / duration) * 100);
  }
}

function nextIndex() {
  if (!tracks.length) return -1;
  if (shuffle && tracks.length > 1) {
    let index = currentIndex;
    while (index === currentIndex) {
      index = Math.floor(Math.random() * tracks.length);
    }
    return index;
  }
  if (currentIndex < 0) return 0;
  return currentIndex < tracks.length - 1 ? currentIndex + 1 : 0;
}

function prevIndex() {
  if (!tracks.length) return -1;
  if (shuffle && tracks.length > 1) return nextIndex();
  if (currentIndex < 0) return 0;
  return currentIndex > 0 ? currentIndex - 1 : tracks.length - 1;
}

function formatWhen(ts) {
  const date = new Date(Number(ts) * 1000);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function syncPlayIcon() {
  const icon = playBtn.querySelector("i");
  icon.className = audio.paused ? "fa-solid fa-play" : "fa-solid fa-pause";
  playBtn.title = audio.paused ? "Reproduzir" : "Pausar";
  playBtn.setAttribute("aria-label", playBtn.title);
}

function highlightTrack() {
  libraryEl.querySelectorAll("li").forEach((row, index) => {
    row.classList.toggle("active", index === currentIndex);
  });
}

function coverUrl(name) {
  return `/cover?name=${encodeURIComponent(name)}`;
}

function setPlayerArt(name) {
  if (!name) {
    playerArt.removeAttribute("src");
    playerArt.classList.add("is-hidden");
    return;
  }
  playerArt.classList.remove("is-hidden");
  playerArt.src = coverUrl(name);
}

function updateMediaSession(item) {
  if (!("mediaSession" in navigator) || !item) return;
  const artwork = [{ src: coverUrl(item.name), sizes: "512x512", type: "image/jpeg" }];
  navigator.mediaSession.metadata = new MediaMetadata({
    title: item.title || item.name,
    artist: item.artist || "Playlist",
    album: "Playlist",
    artwork,
  });
  navigator.mediaSession.playbackState = audio.paused ? "paused" : "playing";
}

function updatePositionState() {
  if (!("mediaSession" in navigator) || !navigator.mediaSession.setPositionState) return;
  if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
  try {
    navigator.mediaSession.setPositionState({
      duration: audio.duration,
      playbackRate: audio.playbackRate || 1,
      position: Math.min(audio.currentTime, audio.duration),
    });
  } catch {
    // Some browsers reject position updates while loading.
  }
}

function bindMediaSession() {
  if (!("mediaSession" in navigator)) return;
  const actions = {
    play: () => audio.play().catch(() => {}),
    pause: () => audio.pause(),
    previoustrack: () => {
      const index = prevIndex();
      if (index >= 0) playIndex(index);
    },
    nexttrack: () => {
      const index = nextIndex();
      if (index >= 0) playIndex(index);
    },
    seekto: (details) => {
      if (details.seekTime != null) audio.currentTime = details.seekTime;
    },
    seekbackward: (details) => {
      audio.currentTime = Math.max(0, audio.currentTime - (details.seekOffset || 10));
    },
    seekforward: (details) => {
      const limit = Number.isFinite(audio.duration) ? audio.duration : audio.currentTime;
      audio.currentTime = Math.min(limit, audio.currentTime + (details.seekOffset || 10));
    },
  };
  Object.entries(actions).forEach(([action, handler]) => {
    try {
      navigator.mediaSession.setActionHandler(action, handler);
    } catch {
      // Action not supported in this browser.
    }
  });
}

function playIndex(index) {
  if (index < 0 || index >= tracks.length) return;
  const item = tracks[index];
  currentIndex = index;
  currentName = item.name;
  playerTitle.textContent = item.title || item.name;
  playerArtist.textContent = item.artist || "";
  setPlayerArt(item.name);
  audio.src = `/file?name=${encodeURIComponent(item.name)}`;
  audio.play().catch(() => {});
  highlightTrack();
  syncPlayIcon();
  updateMediaSession(item);
}

function renderLibrary(items) {
  tracks = items;
  libraryEl.replaceChildren();
  libraryEmpty.hidden = items.length > 0;
  items.forEach((item, index) => {
    const li = document.createElement("li");
    li.dataset.name = item.name;
    const title = document.createElement("p");
    title.className = "track-title";
    title.textContent = item.title || item.name;
    const meta = document.createElement("p");
    meta.className = "track-meta";
    meta.textContent = [item.artist, formatWhen(item.downloaded_ts)].filter(Boolean).join(" · ");
    li.append(title, meta);
    li.addEventListener("click", () => playIndex(index));
    libraryEl.append(li);
  });
  if (currentName) {
    currentIndex = tracks.findIndex((item) => item.name === currentName);
    highlightTrack();
  }
}

async function loadLibrary() {
  libraryEmpty.hidden = true;
  libraryEl.replaceChildren();
  try {
    const res = await fetch("/library");
    const data = await res.json();
    libraryEmpty.textContent = "Nenhuma música ainda.";
    renderLibrary(data.items || []);
  } catch {
    libraryEmpty.hidden = false;
    libraryEmpty.textContent = "Não consegui carregar a lista.";
  }
}

function showView(name) {
  const isList = name === "list";
  viewDownload.classList.toggle("is-hidden", isList);
  viewList.classList.toggle("is-hidden", !isList);
  viewTitle.textContent = isList ? "Playlist" : "Download";
  document.querySelectorAll(".tabs button[data-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === name);
  });
  if (isList) loadLibrary();
}

function showToast({ title, artist, thumbnail, name }) {
  toastTrack = { title, artist, thumbnail, name };
  toastTitle.textContent = title || "Faixa";
  toastArtist.textContent = artist || "";
  toastPlay.hidden = !name;
  if (thumbnail) {
    toastArt.hidden = false;
    toastArt.src = thumbnail;
  } else {
    toastArt.removeAttribute("src");
    toastArt.hidden = true;
  }
  requestAnimationFrame(() => toast.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 10000);
}

async function openPlaylist(name, play) {
  showView("list");
  await loadLibrary();
  if (!play || !name) return;
  let index = tracks.findIndex((item) => item.name === name);
  if (index < 0 && toastTrack) {
    tracks.unshift({
      name,
      title: toastTrack.title || name,
      artist: toastTrack.artist || "",
    });
    index = 0;
  }
  if (index >= 0) playIndex(index);
}

async function readFromBrowser() {
  if (!window.isSecureContext || !navigator.clipboard?.readText) {
    return "";
  }
  try {
    return (await navigator.clipboard.readText()).trim();
  } catch {
    return "";
  }
}

async function readFromServer() {
  try {
    const res = await fetch("/clipboard");
    const data = await res.json();
    return (data.text || "").trim();
  } catch {
    return "";
  }
}

async function pasteUrl() {
  setError("");
  const text = (await readFromBrowser()) || (await readFromServer());
  if (text) {
    manual.value = text;
    syncClear();
    manual.focus();
    return;
  }
  manual.focus();
  setError("Clique no campo e pressione Ctrl+V para colar.");
}

async function download() {
  setError("");
  const url = manual.value.trim();
  if (!url) {
    setError("Cole um link para baixar.");
    manual.focus();
    return;
  }

  const fmt = document.querySelector('input[name="fmt"]:checked').value;
  go.disabled = true;
  paste.disabled = true;
  go.textContent = "Baixando…";
  try {
    const res = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, fmt }),
    });
    const data = await res.json();
    if (!data.ok) {
      setError(data.message || "Não foi possível baixar.");
      return;
    }
    manual.value = "";
    syncClear();
    showToast(data);
  } catch {
    setError("Não consegui falar com o servidor local.");
  } finally {
    go.disabled = false;
    paste.disabled = false;
    go.textContent = "Baixar";
  }
}

playBtn.addEventListener("click", () => {
  if (!audio.src) {
    if (tracks.length) playIndex(0);
    return;
  }
  if (audio.paused) audio.play().catch(() => {});
  else audio.pause();
});
prevBtn.addEventListener("click", () => {
  const index = prevIndex();
  if (index >= 0) playIndex(index);
});
nextBtn.addEventListener("click", () => {
  const index = nextIndex();
  if (index >= 0) playIndex(index);
});
shuffleBtn.addEventListener("click", () => {
  shuffle = !shuffle;
  shuffleBtn.classList.toggle("active", shuffle);
});
seek.addEventListener("input", () => {
  seeking = true;
  if (audio.duration) {
    const current = (Number(seek.value) / 100) * audio.duration;
    timeElapsed.textContent = formatTime(current);
    timeLeft.textContent = `-${formatTime(audio.duration - current)}`;
  }
});
seek.addEventListener("change", () => {
  if (audio.duration) audio.currentTime = (Number(seek.value) / 100) * audio.duration;
  seeking = false;
});
audio.addEventListener("play", () => {
  syncPlayIcon();
  if (tracks[currentIndex]) updateMediaSession(tracks[currentIndex]);
  navigator.mediaSession && (navigator.mediaSession.playbackState = "playing");
});
audio.addEventListener("pause", () => {
  syncPlayIcon();
  navigator.mediaSession && (navigator.mediaSession.playbackState = "paused");
});
audio.addEventListener("timeupdate", () => {
  updateTimes();
  updatePositionState();
});
audio.addEventListener("loadedmetadata", () => {
  updateTimes();
  updatePositionState();
});
audio.addEventListener("ended", () => {
  const index = nextIndex();
  if (index >= 0) playIndex(index);
  else syncPlayIcon();
});

document.querySelectorAll(".tabs button[data-view]").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.view));
});
paste.addEventListener("click", pasteUrl);
clear.addEventListener("click", () => {
  manual.value = "";
  setError("");
  syncClear();
  manual.focus();
});
menuBtn.addEventListener("click", (event) => {
  event.stopPropagation();
  toggleMenu();
});
menuPanel.addEventListener("click", (event) => event.stopPropagation());
folderOption.addEventListener("click", pickFolder);
folderForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const path = folderInput.value.trim();
  if (!path) {
    setFolderError("Digite um caminho válido.");
    folderInput.focus();
    return;
  }
  try {
    await saveFolder(path);
    closeMenu();
  } catch (error) {
    setFolderError(error.message);
  }
});
document.addEventListener("click", () => {
  if (!menuPanel.hidden) closeMenu();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !menuPanel.hidden) closeMenu();
});
toast.addEventListener("click", () => {
  if (!toast.classList.contains("show")) return;
  openPlaylist(toastTrack && toastTrack.name, false);
});
toastPlay.addEventListener("click", (event) => {
  event.stopPropagation();
  openPlaylist(toastTrack && toastTrack.name, true);
});
go.addEventListener("click", download);
manual.addEventListener("input", syncClear);
manual.addEventListener("keydown", (event) => {
  if (event.key === "Enter") download();
});
manual.addEventListener("paste", () => {
  setError("");
  requestAnimationFrame(syncClear);
});
playerArt.addEventListener("error", () => {
  playerArt.classList.add("is-hidden");
});
playerArt.addEventListener("load", () => {
  playerArt.classList.remove("is-hidden");
});
syncClear();
bindMediaSession();
loadSettings();
