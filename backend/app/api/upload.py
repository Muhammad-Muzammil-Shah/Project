"""
/api/upload — Resume and JD upload endpoint
Accepts: .tex, .txt, .json files
"""
import os
import json
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Resume, User

router = APIRouter()
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/resume_tailor/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _extract_text(content: bytes, filename: str) -> tuple[str, dict | None]:
    """Extract raw text and optionally parsed JSON from uploaded file."""
    ext = Path(filename).suffix.lower()
    raw = content.decode("utf-8", errors="ignore")

    if ext == ".json":
        try:
            data = json.loads(raw)
            # Flatten JSON to searchable text
            text = " ".join(str(v) for v in _flatten(data))
            return text, data
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON file")

    if ext in (".tex", ".txt", ".md"):
        # Strip LaTeX commands for NLP, keep raw for LaTeX updater
        text = _strip_latex(raw)
        return text, None

    raise HTTPException(400, f"Unsupported file type: {ext}. Use .tex, .txt, or .json")


def _flatten(d: dict | list, prefix: str = "") -> list[str]:
    items: list[str] = []
    if isinstance(d, dict):
        for k, v in d.items():
            items.extend(_flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(d, list):
        for item in d:
            items.extend(_flatten(item, prefix))
    else:
        items.append(str(d))
    return items


def _strip_latex(tex: str) -> str:
    """Remove LaTeX commands, leaving readable text for NLP."""
    import re
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", tex)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    text = re.sub(r"[{}%]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db),
):
    content  = await file.read()
    raw_text, parsed_data = _extract_text(content, file.filename)

    # Save file to disk
    file_id  = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    save_path.write_bytes(content)

    # Store in DB
    resume = Resume(
        user_id      = user_id,
        filename     = file.filename,
        raw_text     = raw_text,
        parsed_data  = parsed_data,
        latex_source = content.decode("utf-8", errors="ignore") if file.filename.endswith(".tex") else None,
        file_path    = str(save_path),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "resume_id":   resume.id,
        "filename":    resume.filename,
        "text_length": len(raw_text),
        "has_latex":   resume.latex_source is not None,
    }


@router.post("/jd")
async def upload_jd(jd_text: str = Form(...)):
    """Accept raw JD text paste — no file required."""
    if len(jd_text) < 50:
        raise HTTPException(400, "Job description too short (min 50 characters)")
    return {"jd_length": len(jd_text), "status": "received"}
