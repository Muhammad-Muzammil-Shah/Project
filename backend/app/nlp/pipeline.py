"""
NLP Pipeline — Keyword Extraction + Semantic Similarity
Uses spaCy for NER/POS + sentence-transformers for embeddings
"""
from __future__ import annotations
import re
from typing import Any
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load models (cached after first call)
_nlp: spacy.Language | None = None
_embedder: SentenceTransformer | None = None

TECH_PATTERNS = [
    # Languages
    r"\b(Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust|Swift|Kotlin|R|SQL)\b",
    # Frameworks
    r"\b(React|Next\.js|FastAPI|Django|Flask|Spring|Node\.js|Express|Vue|Angular)\b",
    # AI/ML
    r"\b(TensorFlow|PyTorch|scikit.learn|HuggingFace|LangChain|OpenAI|spaCy|BERT|GPT)\b",
    # Cloud
    r"\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform|CI/CD|GitHub Actions)\b",
    # Databases
    r"\b(PostgreSQL|MongoDB|Redis|MySQL|Elasticsearch|DynamoDB|Snowflake)\b",
    # Soft skills
    r"\b(leadership|communication|collaboration|problem.solving|agile|scrum|mentoring)\b",
]


def _get_nlp() -> spacy.Language:
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


# ─── Keyword Extraction ──────────────────────────────────────────────────────

def extract_keywords(text: str) -> dict[str, list[str]]:
    """
    Returns structured keywords from job description or resume text.
    Output: {"technical": [...], "roles": [...], "soft_skills": [...], "all": [...]}
    """
    nlp = _get_nlp()
    doc = nlp(text)

    technical: set[str] = set()
    roles:     set[str] = set()

    # Regex-based tech extraction
    for pattern in TECH_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            technical.add(m.strip())

    # spaCy NER for org/product names (often tech tools)
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT"):
            cleaned = ent.text.strip()
            if len(cleaned) > 2:
                technical.add(cleaned)

    # Noun chunks for role extraction (e.g. "senior engineer", "data scientist")
    role_keywords = {"engineer", "developer", "scientist", "analyst", "architect",
                     "manager", "lead", "intern", "consultant", "specialist"}
    for chunk in doc.noun_chunks:
        text_lower = chunk.text.lower()
        if any(kw in text_lower for kw in role_keywords):
            roles.add(chunk.text.strip())

    # Soft skills via regex
    soft_pattern = r"\b(leadership|communication|teamwork|collaboration|problem.solving|agile|scrum|mentoring|analytical|critical.thinking)\b"
    soft_skills = list({m.lower() for m in re.findall(soft_pattern, text, re.IGNORECASE)})

    all_kw = list(technical | roles | set(soft_skills))
    return {
        "technical":   sorted(technical),
        "roles":       sorted(roles),
        "soft_skills": soft_skills,
        "all":         sorted(set(kw.lower() for kw in all_kw)),
    }


# ─── Semantic Matching ───────────────────────────────────────────────────────

def compute_match_score(resume_text: str, jd_text: str) -> dict[str, Any]:
    """
    Returns match score (0-100) and missing keywords.
    """
    embedder = _get_embedder()

    # Overall semantic similarity
    resume_emb = embedder.encode([resume_text])
    jd_emb     = embedder.encode([jd_text])
    similarity = float(cosine_similarity(resume_emb, jd_emb)[0][0])
    score = round(similarity * 100, 1)

    # Keyword-level gap analysis
    jd_kw     = extract_keywords(jd_text)
    resume_kw = extract_keywords(resume_text)

    jd_set     = set(k.lower() for k in jd_kw["all"])
    resume_set = set(k.lower() for k in resume_kw["all"])
    missing    = sorted(jd_set - resume_set)

    # Per-section keyword hits (for dashboard breakdown)
    sections = ["technical", "soft_skills", "roles"]
    breakdown: dict[str, float] = {}
    for sec in sections:
        jd_sec  = set(k.lower() for k in jd_kw.get(sec, []))
        res_sec = set(k.lower() for k in resume_kw.get(sec, []))
        if jd_sec:
            breakdown[sec] = round(len(jd_sec & res_sec) / len(jd_sec) * 100, 1)
        else:
            breakdown[sec] = 100.0

    return {
        "match_score":    score,
        "missing_skills": missing,
        "jd_keywords":    jd_kw,
        "resume_keywords": resume_kw,
        "breakdown":      breakdown,
    }
