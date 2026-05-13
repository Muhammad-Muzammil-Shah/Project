"""
Resume Tailoring API — FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, analyze, generate, compile, history

app = FastAPI(
    title="Resume Tailor API",
    description="AI-powered resume tailoring with LaTeX output",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router,   prefix="/api/upload",   tags=["Upload"])
app.include_router(analyze.router,  prefix="/api/analyze",  tags=["Analysis"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(compile.router,  prefix="/api/compile",  tags=["Compile"])
app.include_router(history.router,  prefix="/api/history",  tags=["History"])

@app.get("/")
def root():
    return {"status": "Resume Tailor API running", "version": "1.0.0"}
