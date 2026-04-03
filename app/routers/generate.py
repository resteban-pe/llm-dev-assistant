import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.config import llm_provider
from app.llm_provider import LLMTimeoutError

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
        result, tokens = llm_provider.complete(
            system=PROMPT_STRUCTURE,
            user=f"Project: {req.project_name}\nDomain: {req.domain_description}",
        )
        logger.info("generate_structure | tokens_used=%d", tokens)
        return GenerateResponse(result=result, tokens_used=tokens)
    except LLMTimeoutError:
        logger.error("generate_structure | timeout")
        raise HTTPException(status_code=504, detail="El proveedor LLM no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_structure | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar la estructura.")


@router.post("/generate/tests", response_model=GenerateResponse)
def generate_tests(req: TestsRequest):
    logger.info("generate_tests | class=%s", req.class_name)
    try:
        result, tokens = llm_provider.complete(
            system=PROMPT_TESTS,
            user=f"Class name: {req.class_name}\n\n{req.java_class}",
        )
        logger.info("generate_tests | tokens_used=%d", tokens)
        return GenerateResponse(result=result, tokens_used=tokens)
    except LLMTimeoutError:
        logger.error("generate_tests | timeout")
        raise HTTPException(status_code=504, detail="El proveedor LLM no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_tests | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar los tests.")


@router.post("/generate/docs", response_model=GenerateResponse)
def generate_docs(req: DocsRequest):
    logger.info("generate_docs | api_title=%s endpoints=%d", req.api_title, len(req.endpoints))
    try:
        endpoints_text = "\n".join(f"- {ep}" for ep in req.endpoints)
        result, tokens = llm_provider.complete(
            system=PROMPT_DOCS,
            user=f"API Title: {req.api_title}\n\nEndpoints:\n{endpoints_text}",
        )
        logger.info("generate_docs | tokens_used=%d", tokens)
        return GenerateResponse(result=result, tokens_used=tokens)
    except LLMTimeoutError:
        logger.error("generate_docs | timeout")
        raise HTTPException(status_code=504, detail="El proveedor LLM no respondió a tiempo.")
    except Exception as e:
        logger.error("generate_docs | error=%s", e)
        raise HTTPException(status_code=500, detail="Error interno al generar la documentación.")
