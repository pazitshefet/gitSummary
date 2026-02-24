from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, HttpUrl
from typing import List, Any
import json

from summarizer import summarize_url

app = FastAPI(title="GitHub Repo Summarizer API")

# -------- Request / Response models --------
class SummarizeRequest(BaseModel):
    github_url: HttpUrl


class SummarizeResponse(BaseModel):
    summary: str
    technologies: List[str]
    structure: str


class ErrorResponse(BaseModel):
    status: str
    message: str


# -------- Error handlers in requested format --------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid request body. Expected JSON with field 'github_url' containing a valid URL."
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(status_code=exc.status_code,
                        content={"status": "error", "message": msg})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500,
                        content={"status": "error", "message": f"Internal server error: {str(exc)}"})


# -------- Minimal JSON parser/validator for LLM output --------
def parse_llm_json_output(llm_text: str) -> dict[str, Any]:
    """
    Expect strict JSON from the LLM with keys:
    - summary: str
    - technologies: list[str]
    - structure: str

    but still validate to protect the API contract.
    """
    if not llm_text or not isinstance(llm_text, str):
        raise HTTPException(status_code=500, detail="Summarizer returned empty response")

    raw = llm_text.strip()

    # Optional defensive cleanup if model accidentally wraps in code fences
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500,
                            detail="LLM returned invalid JSON")

    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="LLM JSON response must be an object")

    required = {"summary", "technologies", "structure"}
    missing = required - set(data.keys())
    if missing:
        raise HTTPException(status_code=500,
                            detail=f"LLM JSON missing required fields: {', '.join(sorted(missing))}")

    summary = data.get("summary")
    technologies = data.get("technologies")
    structure = data.get("structure")

    if not isinstance(summary, str):
        raise HTTPException(status_code=500, detail="Field 'summary' must be a string")

    if not isinstance(structure, str):
        raise HTTPException(status_code=500, detail="Field 'structure' must be a string")

    if not isinstance(technologies, list):
        raise HTTPException(status_code=500, detail="Field 'technologies' must be a list of strings")

    # Normalize to list[str]
    technologies = [str(x) for x in technologies if str(x).strip()]

    return {
        "summary": summary.strip(),
        "technologies": technologies,
        "structure": structure.strip(),
    }


# -------- Endpoint --------
@app.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def summarize_repo(payload: SummarizeRequest):
    github_url = str(payload.github_url)
    llm_text = summarize_url(github_url)
    return parse_llm_json_output(llm_text)