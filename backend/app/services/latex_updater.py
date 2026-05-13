"""
LaTeX Updater — Dynamically rewrites LaTeX resume sections
to match job description keywords and ATS requirements.
"""
from __future__ import annotations
import re
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ─── Section Parsers ─────────────────────────────────────────────────────────

def extract_latex_sections(latex: str) -> dict[str, str]:
    """Parse LaTeX into named sections for targeted rewriting."""
    sections: dict[str, str] = {}

    # Match \begin{section}...\end{section} style blocks
    for name in ["summary", "experience", "education", "skills", "projects", "certifications"]:
        pattern = rf"(\\section\{{[^}}]*{name}[^}}]*\}})(.*?)(?=\\section\{{|\\end\{{document\}})"
        match = re.search(pattern, latex, re.IGNORECASE | re.DOTALL)
        if match:
            sections[name] = match.group(0)

    # Extract header placeholders
    header_match = re.search(r"\\simpleheader\{[^}]*\}(\{[^}]*\})*", latex)
    if header_match:
        sections["header"] = header_match.group(0)

    return sections


def update_simpleheader(latex: str, name: str, role: str, contact: dict) -> str:
    """Update \\simpleheader{name}{role}{email}{phone}{location}"""
    new_header = (
        f"\\simpleheader{{{name}}}{{{role}}}"
        f"{{{contact.get('email', '')}}}"
        f"{{{contact.get('phone', '')}}}"
        f"{{{contact.get('location', '')}}}"
    )
    return re.sub(r"\\simpleheader\{[^{}]*\}(\{[^{}]*\})*", new_header, latex)


def update_skills_bar(latex: str, skills: list[dict]) -> str:
    """
    Update \\barrule{skill}{proficiency} entries.
    skills = [{"name": "Python", "level": 0.9}, ...]
    """
    new_skills = "\n".join(
        f"\\barrule{{{s['name']}}}{{{int(s['level'] * 100)}}}"
        for s in skills
    )
    # Replace existing skill bars block
    return re.sub(
        r"(% SKILLS_START)(.*?)(% SKILLS_END)",
        f"\\1\n{new_skills}\n\\3",
        latex,
        flags=re.DOTALL,
    )


# ─── AI Section Rewriter ─────────────────────────────────────────────────────

def rewrite_section_with_ai(
    section_name: str,
    original_content: str,
    jd_text: str,
    missing_keywords: list[str],
) -> str:
    """
    Use Claude to rewrite a resume section to better match the JD.
    Returns updated section text (LaTeX-compatible).
    """
    missing_str = ", ".join(missing_keywords[:15]) if missing_keywords else "none"

    prompt = f"""You are an expert resume writer and ATS optimization specialist.

TASK: Rewrite the {section_name.upper()} section of a LaTeX resume to better match a job description.

STRICT RULES:
1. Keep valid LaTeX syntax — preserve all \\commands, {{braces}}, and formatting
2. ATS-friendly: no icons, no tables, plain readable text only
3. Add these missing keywords naturally: {missing_str}
4. Use strong action verbs (Led, Built, Optimized, Delivered, Architected)
5. Include measurable achievements where possible (e.g., "improved performance by 40%")
6. Do NOT fabricate specific companies, dates, or metrics — only enhance existing ones
7. Keep roughly the same length as the original
8. Return ONLY the LaTeX code — no explanation, no markdown fences

JOB DESCRIPTION (key requirements):
{jd_text[:1500]}

ORIGINAL {section_name.upper()} SECTION:
{original_content}

REWRITTEN {section_name.upper()} SECTION:"""

    message = client.chat.completions.create(
        model="llama3-70b-8192",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.choices[0].message.content.strip()


def generate_tailored_summary(jd_text: str, resume_data: dict, target_role: str) -> str:
    """Generate a new professional summary targeting the JD."""
    name      = resume_data.get("name", "the candidate")
    skills    = resume_data.get("skills", [])
    exp_years = resume_data.get("experience_years", "several")

    prompt = f"""Write a 3-sentence professional summary for a LaTeX resume.

Candidate: {name}
Target role: {target_role}
Years of experience: {exp_years}
Key skills: {', '.join(skills[:10])}

Job Description snippet:
{jd_text[:800]}

Rules:
- Start with a strong role identifier (e.g., "AI Engineer with 3+ years...")
- Include 2-3 relevant technical keywords from the JD
- End with a value proposition (what you bring to the team)
- ATS-friendly plain text — no LaTeX formatting needed here
- Return ONLY the 3-sentence summary"""

    message = client.chat.completions.create(
        model="llama3-70b-8192",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.choices[0].message.content.strip()


# ─── Main Tailoring Orchestrator ─────────────────────────────────────────────

def tailor_latex_resume(
    original_latex: str,
    jd_text: str,
    analysis: dict,
    resume_data: dict,
) -> str:
    """
    Full pipeline: analyze → rewrite sections → inject keywords → return tailored LaTeX.
    
    analysis keys: match_score, missing_skills, jd_keywords, breakdown
    resume_data keys: name, role, contact, skills, experience_years
    """
    tailored = original_latex
    missing  = analysis.get("missing_skills", [])

    # 1. Update header if contact info is available
    if resume_data.get("contact"):
        tailored = update_simpleheader(
            tailored,
            resume_data.get("name", ""),
            resume_data.get("target_role", resume_data.get("role", "")),
            resume_data["contact"],
        )

    # 2. Rewrite Summary section
    sections = extract_latex_sections(tailored)
    if "summary" in sections:
        new_summary = rewrite_section_with_ai("summary", sections["summary"], jd_text, missing)
        tailored = tailored.replace(sections["summary"], new_summary)

    # 3. Rewrite Experience section
    if "experience" in sections:
        new_exp = rewrite_section_with_ai("experience", sections["experience"], jd_text, missing)
        tailored = tailored.replace(sections["experience"], new_exp)

    # 4. Rewrite Projects section
    if "projects" in sections:
        new_proj = rewrite_section_with_ai("projects", sections["projects"], jd_text, missing[:5])
        tailored = tailored.replace(sections["projects"], new_proj)

    # 5. Update skill bars — prioritize JD-matching skills
    jd_tech = analysis.get("jd_keywords", {}).get("technical", [])
    resume_skills = resume_data.get("skills", [])
    # Reorder: JD-matching skills first
    ordered_skills = []
    for s in jd_tech[:5]:
        ordered_skills.append({"name": s, "level": 0.85})
    for s in resume_skills:
        if s not in jd_tech:
            ordered_skills.append({"name": s, "level": 0.75})
    if ordered_skills:
        tailored = update_skills_bar(tailored, ordered_skills[:12])

    return tailored
