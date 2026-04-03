import os
from dotenv import load_dotenv
from app.llm_provider import LLMProvider, AnthropicProvider, OpenAIProvider

load_dotenv()

LLM_PROVIDER_NAME = os.getenv("LLM_PROVIDER", "anthropic").lower()
PORT = int(os.getenv("PORT", 8083))

MAX_TOKENS = 2048
TIMEOUT    = 60.0

_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai":    "gpt-4o",
}


def _build_provider() -> LLMProvider:
    model = _MODELS.get(LLM_PROVIDER_NAME)
    if LLM_PROVIDER_NAME == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no está configurada. Agrégala en .env o como variable de entorno.")
        return AnthropicProvider(model=model, max_tokens=MAX_TOKENS, timeout=TIMEOUT)
    if LLM_PROVIDER_NAME == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada. Agrégala en .env o como variable de entorno.")
        return OpenAIProvider(model=model, max_tokens=MAX_TOKENS, timeout=TIMEOUT)
    raise ValueError(f"LLM_PROVIDER '{LLM_PROVIDER_NAME}' no soportado. Valores válidos: 'anthropic', 'openai'.")


llm_provider: LLMProvider = _build_provider()
