from PySide6.QtCore import QThread, Signal


class ChatWorker(QThread):
    token = Signal(str)
    finished_text = Signal(str)
    error = Signal(str)

    def __init__(self, brain, messages):
        super().__init__()
        self.brain = brain
        self.messages = messages

    def run(self):
        full = ""
        try:
            for chunk in self.brain.stream_chat(self.messages):
                full += chunk
                self.token.emit(chunk)
        except Exception as e:  # noqa: BLE001 - surfaced to the UI
            self.error.emit(str(e))
            return
        self.finished_text.emit(full)


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
