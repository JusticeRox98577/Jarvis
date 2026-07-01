import datetime
from html import escape

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jarvis.config import resolve_data_dir
from jarvis.core.llm import OllamaBrain
from jarvis.core.memory import Memory
from jarvis.core.system_stats import get_stats
from jarvis.core.tools import try_handle
from jarvis.ui.hud_widgets import ArcReactorWidget, GaugeRing, HudBackground
from jarvis.ui.theme import CYAN, CYAN_DIM, CYAN_GLOW, GREEN, STYLESHEET
from jarvis.workers import ChatWorker, ListenWorker, SpeakWorker

try:
    from jarvis.core.stt import SpeechToText
    _STT_AVAILABLE = True
except ImportError:
    _STT_AVAILABLE = False

try:
    from jarvis.core.tts import TextToSpeech
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False


class MainWindow(QWidget):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle(cfg.app.name)
        self.setStyleSheet(STYLESHEET)

        data_dir = resolve_data_dir(cfg)
        self.memory = Memory(data_dir, max_turns=cfg.app.max_history_turns)
        self.brain = OllamaBrain(
            host=cfg.ollama.host,
            model=cfg.ollama.model,
            system_prompt=cfg.ollama.system_prompt,
            temperature=cfg.ollama.temperature,
        )

        self.stt = None
        self.tts = None
        self.voice_enabled = bool(cfg.voice.enabled)

        self._chat_worker = None
        self._speak_worker = None
        self._listen_worker = None

        self._build_ui()
        self._init_voice()
        QTimer.singleShot(300, self._run_boot_sequence)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(1500)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        bg = HudBackground()
        root.addWidget(bg)
        outer = QVBoxLayout(bg)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- top bar
        top = QHBoxLayout()
        title = QLabel(self.cfg.app.name)
        title.setObjectName("title")
        self.clock_label = QLabel("")
        self.clock_label.setObjectName("clock")
        self.clock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(self.clock_label)
        outer.addLayout(top)

        # --- middle: gauges | reactor | chat
        middle = QHBoxLayout()
        middle.setSpacing(20)

        left = QVBoxLayout()
        left.addWidget(self._panel_header("SYSTEM"))
        self.cpu_gauge = GaugeRing("CPU")
        self.ram_gauge = GaugeRing("RAM")
        self.disk_gauge = GaugeRing("DISK")
        left.addWidget(self.cpu_gauge)
        left.addWidget(self.ram_gauge)
        left.addWidget(self.disk_gauge)
        left.addStretch(1)
        left.addWidget(self._panel_header(f"MODEL: {self.cfg.ollama.model}"))
        middle.addLayout(left, 0)

        center = QVBoxLayout()
        center.addStretch(1)
        self.reactor = ArcReactorWidget()
        center.addWidget(self.reactor, 0, Qt.AlignCenter)
        self.status_label = QLabel("ONLINE")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignCenter)
        center.addWidget(self.status_label)
        center.addStretch(1)
        middle.addLayout(center, 1)

        right = QVBoxLayout()
        right.addWidget(self._panel_header("COMM LOG"))
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        right.addWidget(self.chat_log, 1)
        middle.addLayout(right, 1)

        outer.addLayout(middle, 1)

        # --- bottom input bar
        bottom = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Speak, or type a command...")
        self.input_box.returnPressed.connect(self._on_send_clicked)
        bottom.addWidget(self.input_box, 1)

        self.mic_button = QPushButton("MIC")
        self.mic_button.setCheckable(True)
        self.mic_button.clicked.connect(self._on_mic_toggled)
        bottom.addWidget(self.mic_button)

        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self._on_send_clicked)
        bottom.addWidget(self.send_button)

        outer.addLayout(bottom)

    def _panel_header(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("panelHeader")
        return lbl

    # --------------------------------------------------------------- voice

    def _init_voice(self):
        if not self.voice_enabled:
            self.mic_button.setEnabled(False)
            self.mic_button.setToolTip("Voice disabled in config.yaml")
            return
        if not _STT_AVAILABLE or not _TTS_AVAILABLE:
            self.mic_button.setEnabled(False)
            self.mic_button.setToolTip(
                "Voice dependencies not installed (faster-whisper / sounddevice / pyttsx3)."
            )
            return
        try:
            self.stt = SpeechToText(
                model_size=self.cfg.voice.stt_model,
                device=self.cfg.voice.stt_device,
            )
            self.tts = TextToSpeech(
                rate=self.cfg.voice.tts_rate,
                voice_hint=self.cfg.voice.tts_voice_hint,
            )
        except Exception as exc:  # noqa: BLE001
            self.mic_button.setEnabled(False)
            self.mic_button.setToolTip(f"Voice init failed: {exc}")
            self.stt = None
            self.tts = None

    # ------------------------------------------------------------- boot

    def _run_boot_sequence(self):
        self._append_system_line("INITIALIZING J.A.R.V.I.S. ...", CYAN_DIM)
        connected = self.brain.check_connection()
        if connected:
            self._append_system_line(f"CONNECTED TO OLLAMA @ {self.cfg.ollama.host}", GREEN)
            self._append_system_line(f"MODEL LOADED: {self.cfg.ollama.model}", GREEN)
        else:
            self._append_system_line(
                f"CANNOT REACH OLLAMA @ {self.cfg.ollama.host} — run 'ollama serve' and 'ollama pull {self.cfg.ollama.model}'",
                "#ff5555",
            )
        self._append_system_line("ALL SYSTEMS ONLINE.", CYAN)
        self.status_label.setText("ONLINE")

    # ------------------------------------------------------------- clock

    def _update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%A  %d %B %Y   %H:%M:%S"))

    def _update_stats(self):
        stats = get_stats()
        self.cpu_gauge.set_value(stats["cpu"])
        self.ram_gauge.set_value(stats["ram"])
        self.disk_gauge.set_value(stats["disk"])

    # -------------------------------------------------------- chat log UI

    def _append_user_message(self, text: str):
        self.chat_log.moveCursor(QTextCursor.End)
        self.chat_log.insertHtml(
            f'<br><span style="color:{GREEN};font-weight:bold;">&gt;&gt; YOU:</span> {escape(text)}<br>'
        )
        self.chat_log.ensureCursorVisible()

    def _start_assistant_line(self):
        self.chat_log.moveCursor(QTextCursor.End)
        self.chat_log.insertHtml(
            f'<br><span style="color:{CYAN};font-weight:bold;">J.A.R.V.I.S.:</span> '
        )
        self.chat_log.ensureCursorVisible()

    def _append_assistant_token(self, token: str):
        cursor = self.chat_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self.chat_log.setTextCursor(cursor)
        self.chat_log.ensureCursorVisible()

    def _append_system_line(self, text: str, color: str = CYAN_DIM):
        self.chat_log.moveCursor(QTextCursor.End)
        self.chat_log.insertHtml(f'<br><span style="color:{color};">[{escape(text)}]</span>')
        self.chat_log.ensureCursorVisible()

    # ----------------------------------------------------------- actions

    def _on_send_clicked(self):
        text = self.input_box.text().strip()
        if not text:
            return
        self.input_box.clear()
        self._handle_user_message(text)

    def _handle_user_message(self, text: str):
        self._append_user_message(text)
        self.memory.add("user", text)

        tool_reply = try_handle(text)
        if tool_reply is not None:
            self.memory.add("assistant", tool_reply)
            self._start_assistant_line()
            self._append_assistant_token(tool_reply)
            self._speak(tool_reply)
            return

        self.reactor.set_state("thinking")
        self.status_label.setText("THINKING")
        self.send_button.setEnabled(False)
        self._start_assistant_line()

        self._chat_worker = ChatWorker(self.brain, self.memory.context())
        self._chat_worker.token.connect(self._append_assistant_token)
        self._chat_worker.finished_text.connect(self._on_chat_finished)
        self._chat_worker.error.connect(self._on_chat_error)
        self._chat_worker.start()

    def _on_chat_finished(self, full_text: str):
        self.memory.add("assistant", full_text)
        self.send_button.setEnabled(True)
        self._speak(full_text)

    def _on_chat_error(self, message: str):
        self._append_assistant_token(f"(connection error: {message})")
        self.send_button.setEnabled(True)
        self.reactor.set_state("idle")
        self.status_label.setText("ONLINE")

    def _speak(self, text: str):
        if not (self.voice_enabled and self.tts and self.cfg.voice.tts_enabled):
            self.reactor.set_state("idle")
            self.status_label.setText("ONLINE")
            return
        self.reactor.set_state("speaking")
        self.status_label.setText("SPEAKING")
        self._speak_worker = SpeakWorker(self.tts, text)
        self._speak_worker.done.connect(self._on_speak_done)
        self._speak_worker.start()

    def _on_speak_done(self):
        self.reactor.set_state("idle")
        self.status_label.setText("ONLINE")

    def _on_mic_toggled(self, checked: bool):
        if not self.stt:
            return
        if checked:
            self.mic_button.setText("STOP")
            self.reactor.set_state("listening")
            self.status_label.setText("LISTENING")
            self.stt.start()
        else:
            self.mic_button.setText("MIC")
            self.status_label.setText("TRANSCRIBING")
            self._listen_worker = ListenWorker(self.stt)
            self._listen_worker.transcribed.connect(self._on_transcribed)
            self._listen_worker.error.connect(self._on_chat_error)
            self._listen_worker.start()

    def _on_transcribed(self, text: str):
        self.reactor.set_state("idle")
        self.status_label.setText("ONLINE")
        text = text.strip()
        if not text:
            self._append_system_line("(no speech detected)")
            return
        self._handle_user_message(text)
