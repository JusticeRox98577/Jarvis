"""Lightweight local intent router.

A handful of commands are handled instantly without touching the LLM
(faster, and works even if Ollama is unreachable). Anything else falls
through to the model.
"""
import datetime
import subprocess
import webbrowser

_APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "files": "explorer.exe",
    "task manager": "taskmgr.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "chrome": "chrome.exe",
}


def try_handle(text: str):
    """Return a canned response string if this text is a known local
    command, otherwise None (meaning: send it to the LLM)."""
    t = text.lower().strip().rstrip("?.!")

    if any(p in t for p in ("what time is it", "current time", "tell me the time")):
        return f"It's {datetime.datetime.now().strftime('%I:%M %p')}, sir."

    if any(p in t for p in ("what's the date", "what is the date", "today's date", "what day is it")):
        return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

    if t.startswith("open "):
        return _open_app(t[len("open "):].strip())

    if t.startswith("search for "):
        return _web_search(t[len("search for "):].strip())

    if t.startswith("google "):
        return _web_search(t[len("google "):].strip())

    return None


def _web_search(query: str):
    if not query:
        return None
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching the web for '{query}', sir."


def _open_app(name: str):
    if not name:
        return None
    if name in ("browser", "web browser", "internet"):
        webbrowser.open("https://www.google.com")
        return "Opening your browser, sir."
    exe = _APP_MAP.get(name, f"{name}.exe")
    try:
        subprocess.Popen(exe, shell=True)
        return f"Opening {name}, sir."
    except OSError:
        return f"I couldn't find '{name}' on this system, sir."
