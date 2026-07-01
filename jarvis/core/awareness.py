"""Opt-in foreground-window awareness.

This reads only the OS-reported window TITLE and owning process name of
whatever window currently has focus -- never keystrokes, never screen
pixels, never clipboard content, never browsing history. Nothing here is
ever written to disk; callers are expected to keep only the latest title
in memory for the current session. Anything matching the caller-supplied
blocklist is skipped entirely and never returned.
"""

try:
    import psutil
    import win32gui
    import win32process

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def is_available() -> bool:
    return _AVAILABLE


def get_active_window(blocklist):
    if not _AVAILABLE:
        return None
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = (win32gui.GetWindowText(hwnd) or "").strip()
        if not title:
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc_name = psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = ""
        haystack = f"{title} {proc_name}".lower()
        if any(term.lower() in haystack for term in blocklist):
            return None
        return title
    except Exception:
        return None
