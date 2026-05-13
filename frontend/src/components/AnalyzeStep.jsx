import { useEffect, useState } from "react";
import { ScoreRing, KeywordChips } from "./ScoreRing";

export default function AnalyzeStep({ resume, onComplete }) {
  const [status,   setStatus]   = useState("analyzing"); // analyzing | done | error
  const [analysis, setAnalysis] = useState(null);
  const [error,    setError]    = useState("");

  useEffect(() => {
    if (!resume) return;
    // resume already has analysis data from UploadStep (analyze runs immediately after upload)
    if (resume.match_score !== undefined) {
      setAnalysis(resume);
      setStatus("done");
    } else {
      setError("No analysis data returned. Please try uploading again.");
      setStatus("error");
    }
  }, [resume]);

  if (status === "analyzing") {
    return (
      <div className="step-container" style={{ textAlign: "center", padding: "4rem 0" }}>
        <div className="spinner" />
        <h2 style={{ marginTop: "1.5rem" }}>Analyzing your resume…</h2>
        <p className="muted">Running NLP keyword extraction and semantic matching</p>
        <div className="progress-steps">
          {["Extracting JD keywords", "Parsing resume sections", "Computing semantic similarity", "Identifying skill gaps"].map((s, i) => (
            <div key={i} className="progress-step">
              <span className="step-dot animating" style={{ animationDelay: `${i * 0.4}s` }} />
              <span className="muted small">{s}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="step-container">
        <div className="error-banner">⚠️ {error}</div>
        <button className="btn-primary" onClick={() => window.location.reload()}>Start Over</button>
      </div>
    );
  }

  const { match_score = 0, missing_skills = [], jd_keywords = {}, breakdown = {}, session_id } = analysis;
  const scoreColor = match_score >= 75 ? "#1D9E75" : match_score >= 50 ? "#EF9F27" : "#D85A30";

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Analysis Complete ✅</h1>
        <p className="muted">Here's how your resume matches the job description.</p>
      </div>

      {/* Score summary */}
      <div className="card" style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
        <ScoreRing score={match_score} color={scoreColor} />
        <div style={{ flex: 1 }}>
          <h2 style={{ marginBottom: "0.25rem" }}>Keyword Match Score</h2>
          <p style={{ color: scoreColor, fontWeight: 600, marginBottom: "1rem" }}>
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

      {/* Missing skills */}
      {missing_skills.length > 0 && (
        <div className="card">
          <h2 className="card-title">🚨 Missing Keywords — AI will add these</h2>
          <KeywordChips keywords={missing_skills.slice(0, 20)} variant="danger" />
        </div>
      )}

      {/* JD keywords found */}
      <div className="card">
        <h2 className="card-title">✅ Technical Keywords in JD</h2>
        <KeywordChips keywords={jd_keywords.technical || []} variant="success" />
      </div>

      <div className="action-row">
        <button
          className="btn-primary large"
          onClick={() => onComplete({ ...analysis, session_id })}
        >
          Continue to Dashboard →
        </button>
      </div>

      <style>{`
        .spinner {
          width: 48px; height: 48px;
          border: 3px solid #e8e7e2;
          border-top-color: #378ADD;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin: 0 auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .progress-steps { margin-top: 2rem; display: flex; flex-direction: column; gap: 12px; align-items: center; }
        .progress-step { display: flex; align-items: center; gap: 10px; }
        .step-dot {
          width: 8px; height: 8px; border-radius: 50%; background: #378ADD;
          animation: pulse 1.2s ease-in-out infinite;
        }
        @keyframes pulse { 0%,100%{opacity:0.3} 50%{opacity:1} }
      `}</style>
    </div>
  );
}
