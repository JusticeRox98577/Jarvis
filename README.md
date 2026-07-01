# J.A.R.V.I.S.

A native Windows desktop assistant in the classic Tony Stark blue-HUD style,
running entirely on your own hardware via [Ollama](https://ollama.com) — no
cloud, no API keys, no data leaving your PC.

- Animated arc-reactor core that reacts to state (idle / listening / thinking / speaking)
- Live CPU / RAM / disk gauge rings
- Local LLM brain via Ollama, streamed token-by-token
- Push-to-talk voice input (local Whisper) and offline text-to-speech reply
- A few built-in commands (time, date, open an app, web search) that don't need the LLM
- Conversation memory persisted across sessions

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

Pull a model for Ollama if you haven't already (in a separate terminal):

```bat
ollama pull llama3.1:8b
```

Your 7900XT has 20GB of VRAM, so you have room to size up. Rough guide:

| Model                          | Feel                          |
|---------------------------------|--------------------------------|
| `llama3.1:8b`                   | Fast, snappy, default          |
| `qwen2.5:14b`                   | Noticeably smarter, still fast |
| `qwen2.5:32b-instruct-q4_K_M`   | Best quality, slower per token |

Set whichever you like in `config.yaml` under `ollama.model`, then re-run
`run.bat`.

## Getting updates later

Whenever there's a new version of this app, pull it before running again:

```bat
git pull origin main
run.bat
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
| `app.max_history_turns`      | How much conversation context is sent to the model each turn          |

## Using it

- Type in the box and hit Enter/SEND, or click **MIC** to talk, click **STOP**
  to send what you said.
- Built-in commands that skip the LLM entirely: "what time is it", "what's
  the date", "open notepad" (or calculator/explorer/chrome/etc.), "search for
  ...".
- Everything else goes to your local model.
- Chat history is saved to `data/history.json` and reloaded next launch.

## Building a standalone .exe

```bat
build_exe.bat
```

Produces `dist\JARVIS\JARVIS.exe` — a double-clickable app, no terminal
window, no need for a Python install on the target machine (Ollama is still
required separately).

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
