"""
/api/history — Retrieve user's tailoring session history
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import TailorSession

router = APIRouter()


@router.get("/{user_id}")
def get_history(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    sessions = (
        db.query(TailorSession)
        .filter(TailorSession.user_id == user_id)
        .order_by(TailorSession.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "session_id":  s.id,
            "match_score": s.match_score,
            "status":      s.status,
            "created_at":  s.created_at.isoformat(),
            "has_pdf":     bool(s.pdf_path),
            "jd_preview":  s.jd_text[:120] + "..." if s.jd_text else "",
        }
        for s in sessions
    ]


@router.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.get(TailorSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "session_id":     session.id,
        "match_score":    session.match_score,
        "missing_skills": session.missing_skills,
        "jd_keywords":    session.jd_keywords,
        "status":         session.status,
        "tailored_latex": session.tailored_latex,
        "pdf_url":        f"/api/compile/download/{session_id}" if session.pdf_path else None,
        "created_at":     session.created_at.isoformat(),
    }
