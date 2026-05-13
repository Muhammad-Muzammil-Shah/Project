"""
/api/compile — Compile tailored LaTeX to PDF via pdflatex
"""
import os
import subprocess
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import TailorSession

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/resume_tailor/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{session_id}")
def compile_to_pdf(session_id: str, db: Session = Depends(get_db)):
    """Compile tailored LaTeX to PDF using pdflatex."""
    session = db.get(TailorSession, session_id)
    if not session or not session.tailored_latex:
        raise HTTPException(404, "No tailored LaTeX found. Run /api/generate first.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "resume.tex"
        tex_file.write_text(session.tailored_latex, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", tmpdir,
                    str(tex_file),
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
        except FileNotFoundError:
            raise HTTPException(
                500,
                "pdflatex not installed. Run: apt-get install texlive-latex-base"
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(500, "LaTeX compilation timed out (>60s)")

        pdf_src = Path(tmpdir) / "resume.pdf"
        if not pdf_src.exists():
            log = (result.stdout or "")[-2000:] + (result.stderr or "")[-500:]
            raise HTTPException(422, f"LaTeX compilation failed:\n{log}")

        # Persist compiled PDF
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


@router.get("/download/{session_id}")
def download_pdf(session_id: str, db: Session = Depends(get_db)):
    """Stream compiled PDF to browser."""
    session = db.get(TailorSession, session_id)
    if not session or not session.pdf_path:
        raise HTTPException(404, "PDF not found. Compile first.")

    pdf_path = Path(session.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(404, "PDF file missing from disk.")

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"tailored_resume_{session_id[:8]}.pdf",
    )
