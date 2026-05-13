// ScoreRing.jsx — Animated SVG score donut
export function ScoreRing({ score = 0, color = "#378ADD" }) {
  const r = 38;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;

  return (
    <svg className="score-ring" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={r} fill="none" stroke="#e8e7e2" strokeWidth="8" />
      <circle
        cx="50" cy="50" r={r}
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        transform="rotate(-90 50 50)"
        style={{ transition: "stroke-dasharray 0.8s ease" }}
      />
      <text x="50" y="45" textAnchor="middle" fontSize="20" fontWeight="600" fill={color}>{score}%</text>
      <text x="50" y="62" textAnchor="middle" fontSize="10" fill="#888">match</text>
    </svg>
  );
}

// KeywordChips.jsx — Chip list for keywords
export function KeywordChips({ keywords = [], variant = "neutral" }) {
  if (!keywords.length) return <p className="muted small">None detected</p>;
  return (
    <div className="chip-group">
      {keywords.map((kw) => (
        <span key={kw} className={`chip ${variant}`}>{kw}</span>
      ))}
    </div>
  );
}

// LaTeXPreview.jsx — Syntax-highlighted LaTeX code block
export function LaTeXPreview({ latex = "" }) {
  const highlighted = latex
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/\\[a-zA-Z]+/g, (m) => `<span style="color:#569cd6">${m}</span>`)
    .replace(/\{([^}]*)\}/g, (_, inner) => `{<span style="color:#ce9178">${inner}</span>}`);

  return (
    <div
      className="latex-preview"
      dangerouslySetInnerHTML={{ __html: highlighted }}
    />
  );
}

// Default export for convenience
export default ScoreRing;
