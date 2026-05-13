"""
/api/analyze — NLP analysis: keyword extraction + match scoring
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Resume, TailorSession
from app.nlp.pipeline import compute_match_score, extract_keywords

router = APIRouter()


class AnalyzeRequest(BaseModel):
    resume_id: str
    jd_text:   str
    user_id:   str


@router.post("/")
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    resume = db.get(Resume, req.resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")

    # Run NLP pipeline
    analysis = compute_match_score(resume.raw_text or "", req.jd_text)

    # Create tailor session
    session = TailorSession(
        user_id         = req.user_id,
        resume_id       = req.resume_id,
        jd_text         = req.jd_text,
        jd_keywords     = analysis["jd_keywords"],
        match_score     = analysis["match_score"],
        missing_skills  = analysis["missing_skills"],
        status          = "analyzed",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id":     session.id,
        "match_score":    analysis["match_score"],
        "missing_skills": analysis["missing_skills"][:20],
        "jd_keywords":    analysis["jd_keywords"],
        "breakdown":      analysis["breakdown"],
        "status":         "analyzed",
    }


@router.get("/keywords")
def get_jd_keywords(jd_text: str):
    """Quick keyword extraction without creating a session."""
    keywords = extract_keywords(jd_text)
    return {"keywords": keywords}
