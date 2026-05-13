import { useState } from "react";
import { generateTailored, compilePDF } from "../utils/api";
import ScoreRing    from "./ScoreRing";
import KeywordChips from "./KeywordChips";
import LaTeXPreview from "./LaTeXPreview";

export default function Dashboard({ session, resume }) {
  const [tailoredLatex, setTailoredLatex] = useState(session?.tailored_latex || null);
  const [generating,    setGenerating]    = useState(false);
  const [compiling,     setCompiling]     = useState(false);
  const [pdfUrl,        setPdfUrl]        = useState(session?.pdf_url || null);
  const [error,         setError]         = useState("");

  if (!session) return <div className="empty-state">No session data. Go back and analyze first.</div>;

  const {
    match_score    = 0,
    missing_skills = [],
    jd_keywords    = {},
    breakdown      = {},
    session_id,
  } = session;

  const handleGenerate = async () => {
    setGenerating(true);
    setError("");
    try {
      const data = await generateTailored(session_id, resume?.resume_data || {});
      setTailoredLatex(data.tailored_latex);
    } catch (e) {
      setError(e.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleCompile = async () => {
    setCompiling(true);
    setError("");
    try {
      const data = await compilePDF(session_id);
      setPdfUrl(data.pdf_url);
    } catch (e) {
      setError(e.message);
    } finally {
      setCompiling(false);
    }
  };

  const scoreColor = match_score >= 75 ? "#1D9E75" : match_score >= 50 ? "#EF9F27" : "#D85A30";

  return (
    <div className="dashboard">
      {/* ── Score Header ─────────────────────────────── */}
      <div className="score-header card">
        <div className="score-left">
          <ScoreRing score={match_score} color={scoreColor} />
        </div>
        <div className="score-right">
          <h2>Match Score</h2>
          <p className="score-label" style={{ color: scoreColor }}>
            {match_score >= 75 ? "Strong Match 🎯" : match_score >= 50 ? "Moderate Match ⚠️" : "Needs Improvement 🔴"}
          </p>
          <div className="breakdown-bars">
            {Object.entries(breakdown).map(([key, val]) => (
              <div key={key} className="breakdown-item">
                <span className="breakdown-label">{key.replace("_", " ")}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${val}%`, background: scoreColor }} />
                </div>
                <span className="breakdown-pct">{val}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Missing Keywords ──────────────────────────── */}
      {missing_skills.length > 0 && (
        <div className="card">
          <h2 className="card-title">🚨 Missing Keywords ({missing_skills.length})</h2>
          <p className="muted">These keywords appear in the JD but not your resume. AI will add them naturally.</p>
          <KeywordChips keywords={missing_skills.slice(0, 20)} variant="danger" />
        </div>
      )}

      {/* ── JD Keywords Found ────────────────────────── */}
      <div className="card">
        <h2 className="card-title">✅ JD Technical Keywords</h2>
        <KeywordChips keywords={jd_keywords.technical || []} variant="success" />
      </div>

      {/* ── Generate Button ───────────────────────────── */}
      {!tailoredLatex && (
        <div className="card generate-card">
          <h2>🤖 Generate Tailored Resume</h2>
          <p className="muted">AI will rewrite your Summary, Experience, and Skills sections to match the JD — keeping valid LaTeX syntax.</p>
          <button className="btn-primary large" onClick={handleGenerate} disabled={generating}>
            {generating ? "✨ Generating with AI…" : "Generate Tailored Resume"}
          </button>
        </div>
      )}

      {/* ── LaTeX Preview ─────────────────────────────── */}
      {tailoredLatex && (
        <div className="card">
          <div className="preview-header">
            <h2 className="card-title">📝 Tailored LaTeX Preview</h2>
            <div className="preview-actions">
              <button className="btn-secondary" onClick={handleGenerate} disabled={generating}>
                {generating ? "Regenerating…" : "↺ Regenerate"}
              </button>
              <button className="btn-primary" onClick={handleCompile} disabled={compiling}>
                {compiling ? "Compiling PDF…" : "⬇ Compile to PDF"}
              </button>
            </div>
          </div>
          <LaTeXPreview latex={tailoredLatex} />
        </div>
      )}

      {/* ── PDF Download ──────────────────────────────── */}
      {pdfUrl && (
        <div className="card success-card">
          <h2>🎉 Your PDF is Ready!</h2>
          <p className="muted">ATS-optimized, clean formatting, all keywords included.</p>
          <a
            className="btn-primary large"
            href={`${import.meta.env.VITE_API_URL}${pdfUrl}`}
            download
            target="_blank"
            rel="noopener noreferrer"
          >
            ⬇ Download PDF Resume
          </a>
        </div>
      )}

      {error && <div className="error-banner">⚠️ {error}</div>}
    </div>
  );
}
