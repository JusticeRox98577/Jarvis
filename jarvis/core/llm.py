import ollama


class OllamaBrain:
    """Thin wrapper around a local Ollama server."""

    def __init__(self, host: str, model: str, system_prompt: str, temperature: float = 0.7):
        self.client = ollama.Client(host=host)
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature

    def check_connection(self) -> bool:
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def stream_chat(self, messages):
        """Yield response text chunks for the given conversation history."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + list(messages)
        stream = self.client.chat(
            model=self.model,
            messages=full_messages,
            stream=True,
            options={"temperature": self.temperature},
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
