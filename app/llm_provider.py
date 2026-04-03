from abc import ABC, abstractmethod


class LLMTimeoutError(Exception):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str) -> tuple[str, int]:
        """Returns (result_text, tokens_used)."""


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str, max_tokens: int, timeout: float):
        import anthropic
        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens
        self._timeout = timeout

    def complete(self, system: str, user: str) -> tuple[str, int]:
        import anthropic
        try:
            msg = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                timeout=self._timeout,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            tokens = msg.usage.input_tokens + msg.usage.output_tokens
            return msg.content[0].text, tokens
        except anthropic.APITimeoutError:
            raise LLMTimeoutError()


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, max_tokens: int, timeout: float):
        from openai import OpenAI
        self._client = OpenAI()
        self._model = model
        self._max_tokens = max_tokens
        self._timeout = timeout

    def complete(self, system: str, user: str) -> tuple[str, int]:
        import openai
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                timeout=self._timeout,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            tokens = resp.usage.total_tokens
            return resp.choices[0].message.content, tokens
        except openai.APITimeoutError:
            raise LLMTimeoutError()
