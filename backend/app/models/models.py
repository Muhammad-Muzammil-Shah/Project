"""
SQLAlchemy models for Resume Tailor
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=gen_uuid)
    email      = Column(String, unique=True, nullable=False, index=True)
    name       = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes    = relationship("Resume", back_populates="user")
    sessions   = relationship("TailorSession", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id           = Column(String, primary_key=True, default=gen_uuid)
    user_id      = Column(String, ForeignKey("users.id"), nullable=False)
    filename     = Column(String, nullable=False)
    raw_text     = Column(Text)           # extracted plain text
    parsed_data  = Column(JSON)           # structured sections dict
    latex_source = Column(Text)           # original LaTeX if uploaded
    file_path    = Column(String)         # path on disk / S3 key
    created_at   = Column(DateTime, default=datetime.utcnow)

    user         = relationship("User", back_populates="resumes")


class TailorSession(Base):
    __tablename__ = "tailor_sessions"

    id              = Column(String, primary_key=True, default=gen_uuid)
    user_id         = Column(String, ForeignKey("users.id"), nullable=False)
    resume_id       = Column(String, ForeignKey("resumes.id"), nullable=False)
    jd_text         = Column(Text, nullable=False)
    jd_keywords     = Column(JSON)           # extracted JD keywords
    match_score     = Column(Float)          # 0-100
    missing_skills  = Column(JSON)           # list of missing keywords
    tailored_latex  = Column(Text)           # updated LaTeX output
    pdf_path        = Column(String)         # compiled PDF path
    status          = Column(String, default="pending")  # pending|analyzing|done|error
    created_at      = Column(DateTime, default=datetime.utcnow)

    user            = relationship("User", back_populates="sessions")
