import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class SpeechToText:
    """Push-to-talk style recorder + local Whisper transcription."""

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8", sample_rate: int = 16000):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.sample_rate = sample_rate
        self._frames = []
        self._stream = None

    def start(self):
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status):
        self._frames.append(indata.copy())

    def stop(self) -> str:
        if self._stream is None:
            return ""
        self._stream.stop()
        self._stream.close()
        self._stream = None
        if not self._frames:
            return ""
        audio = np.concatenate(self._frames, axis=0).flatten()
        segments, _ = self.model.transcribe(audio, language="en")
        return " ".join(seg.text.strip() for seg in segments).strip()
