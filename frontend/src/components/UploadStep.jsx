import { useState, useCallback } from "react";
import { uploadResume } from "../utils/api";

export default function UploadStep({ onComplete }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText,     setJdText]     = useState("");
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState("");
  const [dragOver,   setDragOver]   = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) setResumeFile(file);
  }, []);

  const handleSubmit = async () => {
    if (!resumeFile) { setError("Please upload your resume"); return; }
    if (jdText.length < 50) { setError("Please paste a job description (min 50 chars)"); return; }

    setLoading(true);
    setError("");
    try {
      const data = await uploadResume(resumeFile, jdText);
      onComplete({ ...data, jdText });
    } catch (e) {
      setError(e.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Tailor Your Resume</h1>
        <p className="muted">Upload your resume and paste a job description. AI will optimize it for ATS.</p>
      </div>

      <div className="two-col">
        {/* Resume Upload */}
        <div className="card">
          <h2 className="card-title">📄 Your Resume</h2>
          <div
            className={`drop-zone ${dragOver ? "drag-active" : ""} ${resumeFile ? "has-file" : ""}`}
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => document.getElementById("file-input").click()}
          >
            {resumeFile ? (
              <>
                <span className="file-icon">✅</span>
                <p className="file-name">{resumeFile.name}</p>
                <p className="muted small">{(resumeFile.size / 1024).toFixed(1)} KB</p>
              </>
            ) : (
              <>
                <span className="drop-icon">⬆️</span>
                <p>Drop your resume here</p>
                <p className="muted small">Supports .tex · .txt · .json</p>
              </>
            )}
          </div>
          <input
            id="file-input"
            type="file"
            accept=".tex,.txt,.json"
            hidden
            onChange={(e) => setResumeFile(e.target.files[0])}
          />
          <p className="hint">💡 For best results, upload a <strong>.tex</strong> file — AI will rewrite LaTeX sections directly.</p>
        </div>

        {/* JD Input */}
        <div className="card">
          <h2 className="card-title">💼 Job Description</h2>
          <textarea
            className="jd-textarea"
            placeholder="Paste the full job description here...&#10;&#10;Include: role, requirements, tech stack, responsibilities."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
          <p className="muted small">{jdText.length} characters {jdText.length > 200 ? "✅" : "(min 200 recommended)"}</p>
        </div>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <div className="action-row">
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? "Uploading…" : "Analyze Match →"}
        </button>
      </div>
    </div>
  );
}
