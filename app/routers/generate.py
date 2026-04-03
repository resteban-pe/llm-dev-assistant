import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import anthropic

from app.config import claude_client, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TIMEOUT

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")

PROMPT_STRUCTURE = _load_prompt("generate_structure.md")
PROMPT_TESTS     = _load_prompt("generate_tests.md")
PROMPT_DOCS      = _load_prompt("generate_docs.md")


class StructureRequest(BaseModel):
    domain_description: str
    project_name: str

    @field_validator("domain_description", "project_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()


class TestsRequest(BaseModel):
    java_class: str
    class_name: str

    @field_validator("java_class", "class_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()


class DocsRequest(BaseModel):
    endpoints: list[str]
    api_title: str

    @field_validator("api_title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("endpoints")
    @classmethod
    def endpoints_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("La lista de endpoints no puede estar vacía.")
        if any(not ep.strip() for ep in v):
            raise ValueError("Ningún endpoint puede ser una cadena vacía.")
        return [ep.strip() for ep in v]


class GenerateResponse(BaseModel):
    result: str
    tokens_used: int


@router.post("/generate/structure", response_model=GenerateResponse)
def generate_structure(req: StructureRequest):
    logger.info("generate_structure | project=%s", req.project_name)
    try:
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT,
            system=PROMPT_STRUCTURE,
            messages=[{
                "role": "user",
                "content": f"Project: {req.project_name}\nDomain: {req.domain_description}"
            }]
        )
        tokens = message.usage.input_tokens + message.usage.output_tokens
        logger.info("generate_structure | tokens_used=%d", tokens)
        return GenerateResponse(result=message.content[0].text, tokens_used=tokens)
    except anthropic.APITimeoutError:
        logger.error("generate_structure | timeout after %.1fs", CLAUDE_TIMEOUT)
        raise HTTPException(status_code=504, detail="La API de Claude no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_structure | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar la estructura.")


@router.post("/generate/tests", response_model=GenerateResponse)
def generate_tests(req: TestsRequest):
    logger.info("generate_tests | class=%s", req.class_name)
    try:
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT,
            system=PROMPT_TESTS,
            messages=[{
                "role": "user",
                "content": f"Class name: {req.class_name}\n\n{req.java_class}"
            }]
        )
        tokens = message.usage.input_tokens + message.usage.output_tokens
        logger.info("generate_tests | tokens_used=%d", tokens)
        return GenerateResponse(result=message.content[0].text, tokens_used=tokens)
    except anthropic.APITimeoutError:
        logger.error("generate_tests | timeout after %.1fs", CLAUDE_TIMEOUT)
        raise HTTPException(status_code=504, detail="La API de Claude no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_tests | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar los tests.")


@router.post("/generate/docs", response_model=GenerateResponse)
def generate_docs(req: DocsRequest):
    logger.info("generate_docs | api_title=%s endpoints=%d", req.api_title, len(req.endpoints))
    try:
        endpoints_text = "\n".join(f"- {ep}" for ep in req.endpoints)
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT,
            system=PROMPT_DOCS,
            messages=[{
                "role": "user",
                "content": f"API Title: {req.api_title}\n\nEndpoints:\n{endpoints_text}"
            }]
        )
        tokens = message.usage.input_tokens + message.usage.output_tokens
        logger.info("generate_docs | tokens_used=%d", tokens)
        return GenerateResponse(result=message.content[0].text, tokens_used=tokens)
    except anthropic.APITimeoutError:
        logger.error("generate_docs | timeout after %.1fs", CLAUDE_TIMEOUT)
        raise HTTPException(status_code=504, detail="La API de Claude no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_docs | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar la documentación.")
