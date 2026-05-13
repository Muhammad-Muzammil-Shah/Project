"""
/api/generate — Tailor resume LaTeX using AI
/api/compile  — Compile LaTeX to PDF
"""
import os
import subprocess
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Resume, TailorSession
from app.services.latex_updater import tailor_latex_resume

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/resume_tailor/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Generate Router ──────────────────────────────────────────────────────────
generate_router = APIRouter()


class GenerateRequest(BaseModel):
    session_id:  str
    resume_data: dict   # {name, role, contact:{email,phone,location}, skills:[], experience_years}


@generate_router.post("/")
def generate_tailored_resume(req: GenerateRequest, db: Session = Depends(get_db)):
    session = db.get(TailorSession, req.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    resume = db.get(Resume, session.resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")

    if not resume.latex_source:
        raise HTTPException(400, "No LaTeX source found. Please upload a .tex file.")

    # Run AI tailoring
    analysis = {
        "match_score":    session.match_score,
        "missing_skills": session.missing_skills or [],
        "jd_keywords":    session.jd_keywords or {},
    }

    tailored_latex = tailor_latex_resume(
        original_latex = resume.latex_source,
        jd_text        = session.jd_text,
        analysis       = analysis,
        resume_data    = req.resume_data,
    )

    # Save tailored LaTeX
    session.tailored_latex = tailored_latex
    session.status         = "generated"
    db.commit()

    return {
        "session_id":    session.id,
        "tailored_latex": tailored_latex,
        "status":         "generated",
        "char_count":     len(tailored_latex),
    }


# ── Compile Router ───────────────────────────────────────────────────────────
compile_router = APIRouter()


@compile_router.post("/{session_id}")
def compile_to_pdf(session_id: str, db: Session = Depends(get_db)):
    """Compile tailored LaTeX to PDF using pdflatex."""
    session = db.get(TailorSession, session_id)
    if not session or not session.tailored_latex:
        raise HTTPException(404, "No tailored LaTeX found. Run /generate first.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "resume.tex"
        tex_file.write_text(session.tailored_latex, encoding="utf-8")

        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_file)],
                capture_output=True, text=True, timeout=60, cwd=tmpdir,
            )
        except FileNotFoundError:
            raise HTTPException(500, "pdflatex not installed. Install TeX Live: apt-get install texlive-full")
        except subprocess.TimeoutExpired:
            raise HTTPException(500, "LaTeX compilation timed out")

        pdf_src = Path(tmpdir) / "resume.pdf"
        if not pdf_src.exists():
            log = result.stdout[-2000:] + result.stderr[-500:]
            raise HTTPException(422, f"LaTeX compilation failed:\n{log}")

        # Copy PDF to persistent output
        pdf_dest = OUTPUT_DIR / f"{session_id}.pdf"
        pdf_dest.write_bytes(pdf_src.read_bytes())

        session.pdf_path = str(pdf_dest)
        session.status   = "done"
        db.commit()

    return {
        "session_id": session_id,
        "pdf_url":    f"/api/compile/download/{session_id}",
        "status":     "done",
    }


@compile_router.get("/download/{session_id}")
def download_pdf(session_id: str, db: Session = Depends(get_db)):
    session = db.get(TailorSession, session_id)
    if not session or not session.pdf_path:
        raise HTTPException(404, "PDF not found")

    pdf_path = Path(session.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(404, "PDF file missing from disk")

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"tailored_resume_{session_id[:8]}.pdf",
    )


# Wire routers
router.include_router(generate_router, prefix="")
