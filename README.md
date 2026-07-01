# J.A.R.V.I.S.

A native Windows desktop assistant in the classic Tony Stark blue-HUD style,
running entirely on your own hardware via [Ollama](https://ollama.com) — no
cloud, no API keys, no data leaving your PC.

- Animated arc-reactor core that reacts to state (idle / listening / thinking / speaking)
- Live CPU / RAM / disk gauge rings
- Local LLM brain via Ollama, streamed token-by-token
- Push-to-talk voice input (local Whisper) and offline text-to-speech reply
- A few built-in commands (time, date, open an app, web search) that don't need the LLM
- Long-term memory: recalls relevant past conversations and anything you ask it to remember
- Adaptive personality: tone (verbosity/formality/humor) drifts based on your explicit feedback
- Conversation memory persisted across sessions

## Privacy design

Jarvis does **not** monitor your PC, log keystrokes, capture your screen, or
read your clipboard/browsing history — none of that is in this app, on
purpose. What it does do:

- **Chat memory**: everything you say to it, or explicitly ask it to
  remember, is embedded locally (via Ollama) and stored in
  `data/vector_memory.json` so it can recall relevant context later. Delete
  that file any time to wipe it.
- **Window awareness (off by default)**: if you turn on the **AWARE** button
  (gated by `awareness.enabled: true` in config *and* the button itself),
  Jarvis reads only the *title* of your current foreground window for
  conversational context — e.g. knowing you're in a code editor vs. a game.
  It never reads window contents, keystrokes, or the clipboard, skips
  anything matching `awareness.blocklist` (password managers, banking,
  incognito, etc. by default), and never writes window titles to disk —
  only the single most recent title is held in memory and gone when you
  close the app.

Built for a Windows PC with an AMD Ryzen 9 7900X + Radeon RX 7900XT, but the
app itself is plain Python/Qt and will run wherever Python does.

## Requirements

- Windows 10/11 (64-bit)
- [Python 3.10+](https://www.python.org/downloads/) (check "Add python.exe to PATH" during install)
- [Ollama for Windows](https://ollama.com/download) — recent versions detect
  the 7900XT automatically (RDNA3/gfx1100 is supported out of the box), no
  manual ROCm install needed. Just make sure your AMD Adrenalin drivers are
  up to date.
- A microphone, if you want to use voice

## Quick start

```bat
git clone https://github.com/JusticeRox98577/Jarvis.git
cd Jarvis
run.bat
```

`run.bat` creates a virtual environment, installs dependencies, and launches
the app. First run will take a minute while packages install.

Check what you've already got with `ollama list`, and set `ollama.model` in
`config.yaml` to match (default is `huihui_ai/mistral-small-abliterated:24b`
— pull it with `ollama pull huihui_ai/mistral-small-abliterated:24b`). You'll
also need the small embedding model that powers long-term memory:

```bat
ollama pull nomic-embed-text
```

**Watch VRAM headroom, not just model size.** Your 7900XT has 20GB, but a
model needs room beyond its own file size for context/KV-cache — a ~19GB
model file leaves almost nothing free and will max out VRAM instantly.
Rough guide for this card:

| Model size (file) | Headroom left | Notes                              |
|--------------------|----------------|--------------------------------------|
| ~5GB (`qwen2.5-coder:7b`) | Plenty | Safe, coding-focused |
| ~12GB (`codestral`)       | Comfortable | Stronger, still safe, coding-focused |
| ~14GB (`huihui_ai/mistral-small-abliterated:24b`) | ~6GB free | Default: large, uncensored, general-purpose |
| ~19GB+ (`glm-4.7-flash`, `qwen3-abliterated:30b-a3b`) | Almost none | Maxes out instantly, avoid |

Run `ollama ps` while chatting to see actual VRAM usage if you're unsure.

## Getting updates later

`run.bat` auto-pulls the latest `main` before every launch, so just running
it again gets you up to date — no manual `git pull` needed. If you ever want
to pull without changing directories first, use `git -C`:

```bat
git -C C:\path\to\Jarvis pull origin main
```

(`run.bat` re-installs any new dependencies automatically.)

## Configuration

Edit `config.yaml`:

| Key                        | What it does                                                        |
|-----------------------------|-----------------------------------------------------------------------|
| `ollama.host`               | Ollama server URL (default `http://localhost:11434`)                 |
| `ollama.model`               | Which local model to use                                              |
| `ollama.system_prompt`       | Jarvis's personality                                                  |
| `voice.enabled`              | Master on/off switch for the mic button                              |
| `voice.stt_model`            | Whisper size: `tiny`/`base`/`small`/`medium`                          |
| `voice.tts_enabled`          | Whether Jarvis speaks replies aloud                                    |
| `voice.tts_rate`             | Speech rate                                                            |
| `memory.enabled`             | Turns long-term recall on/off                                          |
| `memory.embed_model`         | Ollama embedding model used for memory (`nomic-embed-text`)            |
| `personality.adapt`          | Whether tone adjusts based on your feedback                            |
| `personality.verbosity/formality/humor` | Starting tone values (0.0-1.0); they drift from there over time |
| `awareness.enabled`          | Master switch for the AWARE button (still requires toggling it in-app) |
| `awareness.blocklist`        | Apps/window titles that are never shared, even when AWARE is on        |
| `app.max_history_turns`      | How much conversation context is sent to the model each turn          |

## Using it

- Type in the box and hit Enter/SEND, or click **MIC** to talk, click **STOP**
  to send what you said.
- Built-in commands that skip the LLM entirely: "what time is it", "what's
  the date", "open notepad" (or calculator/explorer/chrome/etc.), "search for
  ...", "remember that ..." (saves a fact to long-term memory).
- Give style feedback any time — "be more concise", "loosen up", "be more
  formal", "be funnier" — and Jarvis's tone shifts accordingly and stays that
  way.
- Everything else goes to your local model.
- Chat history is saved to `data/history.json` and reloaded next launch.

## Building a real installed Windows app

Two steps turn this from "a Python script you run via `run.bat`" into an
actual installed app with a Start Menu entry, desktop icon, taskbar icon,
and an uninstaller in Add/Remove Programs:

```bat
build_exe.bat
build_installer.bat
```

- `build_exe.bat` produces `dist\JARVIS\JARVIS.exe` — no terminal window, no
  Python install needed on the target machine (Ollama is still required
  separately).
- `build_installer.bat` packages that into `installer_output\JARVIS-Setup.exe`
  using [Inno Setup](https://jrsoftware.org/isdl.php) — install it once
  (default install adds `ISCC.exe` to PATH). Run the generated
  `JARVIS-Setup.exe` and it installs to Program Files, adds Start
  Menu/desktop shortcuts, and registers a normal uninstaller.

Your chat history, memory, and personality settings live in
`%APPDATA%\JARVIS` once installed this way (not in Program Files), so
upgrading or reinstalling never touches them, and the uninstaller leaves
them in place. `config.yaml` gets copied to the install folder on first
install and is never overwritten by upgrades, so your edits stick.

## Troubleshooting

- **"CANNOT REACH OLLAMA"** in the comm log — make sure Ollama is running
  (`ollama serve`, or just launch the Ollama app) and that you've pulled the
  model named in `config.yaml`.
- **MIC button greyed out** — voice dependencies (`faster-whisper`,
  `sounddevice`, `pyttsx3`) failed to install or `voice.enabled` is `false`
  in `config.yaml`. Text chat still works fine.
- **Slow responses** — check `ollama ps` while chatting; if it says `100%
  CPU` instead of using the GPU, update your AMD drivers and Ollama itself,
  then restart `ollama serve`.

## Extending

Local commands live in `jarvis/core/tools.py` — add a new `if`/`elif` branch
in `try_handle()` for anything you want handled instantly without a model
round-trip (opening more apps, controlling media, etc).
