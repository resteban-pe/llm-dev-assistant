import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import anthropic

from app.config import claude_client, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TIMEOUT

logger = logging.getLogger(__name__)

router = APIRouter(tags=["review"])

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")

PROMPT_REVIEW = _load_prompt("review_code.md")


class ReviewRequest(BaseModel):
    code: str
    context: str

    @field_validator("code", "context")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()


class ReviewResponse(BaseModel):
    result: str
    tokens_used: int


@router.post("/review/code", response_model=ReviewResponse)
def review_code(req: ReviewRequest):
    logger.info("review_code | context_len=%d code_len=%d", len(req.context), len(req.code))
    try:
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT,
            system=PROMPT_REVIEW,
            messages=[{
                "role": "user",
                "content": f"Context: {req.context}\n\n{req.code}"
            }]
        )
        tokens = message.usage.input_tokens + message.usage.output_tokens
        logger.info("review_code | tokens_used=%d", tokens)
        return ReviewResponse(result=message.content[0].text, tokens_used=tokens)
    except anthropic.APITimeoutError:
        logger.error("review_code | timeout after %.1fs", CLAUDE_TIMEOUT)
        raise HTTPException(status_code=504, detail="La API de Claude no respondió a tiempo.")
    except Exception as e:
        logger.error("review_code | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al revisar el código.")
