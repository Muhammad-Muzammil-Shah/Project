import { useEffect, useState } from "react";
import { getHistory, getSession } from "../utils/api";

export default function History({ onSelect }) {
  const [sessions, setSessions] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");

  useEffect(() => {
    getHistory()
      .then(setSessions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleOpen = async (sessionId) => {
    try {
      const data = await getSession(sessionId);
      onSelect(data);
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) return <div className="empty-state">Loading history…</div>;
  if (error)   return <div className="error-banner">⚠️ {error}</div>;
  if (!sessions.length) return (
    <div className="empty-state">
      <p style={{ fontSize: "2rem" }}>📭</p>
      <p>No sessions yet. Upload a resume to get started.</p>
    </div>
  );

  const scoreColor = (s) => s >= 75 ? "#1D9E75" : s >= 50 ? "#EF9F27" : "#D85A30";
  const statusIcon = (s) => ({ done: "✅", generated: "🤖", analyzed: "📊", pending: "⏳", error: "❌" }[s] || "⏳");

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Session History</h1>
        <p className="muted">Your past resume tailoring sessions</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {sessions.map((s) => (
          <div key={s.session_id} className="card" style={{ cursor: "pointer" }} onClick={() => handleOpen(s.session_id)}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                  <span style={{ fontSize: "13px" }}>{statusIcon(s.status)}</span>
                  <span style={{ fontWeight: 600, fontSize: "14px" }}>
                    Match: <span style={{ color: scoreColor(s.match_score) }}>{s.match_score}%</span>
                  </span>
                  {s.has_pdf && <span style={{ fontSize: "12px", background: "#EAF3DE", color: "#3B6D11", padding: "2px 8px", borderRadius: "12px" }}>PDF ready</span>}
                </div>
                <p className="muted small" style={{ lineHeight: 1.5 }}>{s.jd_preview}</p>
                <p className="muted small" style={{ marginTop: "4px" }}>
                  {new Date(s.created_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
              <span style={{ color: "#888", fontSize: "18px", marginLeft: "12px" }}>→</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
