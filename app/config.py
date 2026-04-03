import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY no está configurada. Agrégala en .env o como variable de entorno del sistema.")

PORT = int(os.getenv("PORT", 8083))

# Cliente y constantes compartidas entre routers
claude_client  = anthropic.Anthropic()
CLAUDE_MODEL      = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 2048
CLAUDE_TIMEOUT    = 60.0
