import ollama


class OllamaBrain:
    """Thin wrapper around a local Ollama server."""

    def __init__(self, host: str, model: str, system_prompt: str, temperature: float = 0.7, keep_alive: str = "5m"):
        self.client = ollama.Client(host=host)
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.keep_alive = keep_alive

    def check_connection(self) -> bool:
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def stream_chat(self, messages, extra_context: str = ""):
        """Yield response text chunks for the given conversation history.
        extra_context (personality calibration, recalled memory, current
        window title) is folded into the system message for this turn only."""
        system_content = self.system_prompt
        if extra_context:
            system_content = f"{self.system_prompt}\n\n{extra_context}"
        full_messages = [{"role": "system", "content": system_content}] + list(messages)
        stream = self.client.chat(
            model=self.model,
            messages=full_messages,
            stream=True,
            options={"temperature": self.temperature},
            keep_alive=self.keep_alive,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
