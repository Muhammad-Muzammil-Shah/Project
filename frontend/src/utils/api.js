const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USER_ID = "demo-user-001"; // In production, get from auth context

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Request failed: ${res.status}`);
  return data;
}

export async function uploadResume(file, jdText) {
  const form = new FormData();
  form.append("file", file);
  form.append("user_id", USER_ID);

  const uploaded = await request("/api/upload/resume", { method: "POST", body: form });

  // Immediately run analysis
  const analysis = await request("/api/analyze/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_id: uploaded.resume_id,
      jd_text:   jdText,
      user_id:   USER_ID,
    }),
  });

  return {
    resume_id:  uploaded.resume_id,
    has_latex:  uploaded.has_latex,
    session_id: analysis.session_id,
    ...analysis,
  };
}

export async function generateTailored(sessionId, resumeData) {
  return request("/api/generate/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id:  sessionId,
      resume_data: resumeData,
    }),
  });
}

export async function compilePDF(sessionId) {
  return request(`/api/compile/${sessionId}`, { method: "POST" });
}

export async function getHistory() {
  return request(`/api/history/${USER_ID}`);
}

export async function getSession(sessionId) {
  return request(`/api/history/session/${sessionId}`);
}
