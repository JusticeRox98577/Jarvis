from PySide6.QtCore import QThread, Signal


class ChatWorker(QThread):
    token = Signal(str)
    finished_text = Signal(str)
    error = Signal(str)

    def __init__(self, brain, messages, context_fn=None, on_complete=None):
        super().__init__()
        self.brain = brain
        self.messages = messages
        self.context_fn = context_fn
        self.on_complete = on_complete

    def run(self):
        try:
            extra_context = self.context_fn() if self.context_fn else ""
        except Exception:
            extra_context = ""
        full = ""
        try:
            for chunk in self.brain.stream_chat(self.messages, extra_context=extra_context):
                full += chunk
                self.token.emit(chunk)
        except Exception as e:  # noqa: BLE001 - surfaced to the UI
            self.error.emit(str(e))
            return
        self.finished_text.emit(full)
        if self.on_complete:
            try:
                self.on_complete(full)
            except Exception:  # noqa: BLE001 - best-effort memory write
                pass


class SpeakWorker(QThread):
    done = Signal()
    error = Signal(str)

    def __init__(self, tts, text):
        super().__init__()
        self.tts = tts
        self.text = text

    def run(self):
        try:
            self.tts.say(self.text)
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))
        finally:
            self.done.emit()


class ListenWorker(QThread):
    transcribed = Signal(str)
    error = Signal(str)

    def __init__(self, stt):
        super().__init__()
        self.stt = stt

    def run(self):
        try:
            text = self.stt.stop()
            self.transcribed.emit(text)
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))
