import { useState } from "react";
import { getTopicRoadmap, getTopicPapers } from "../api";

export default function TopicRoadmap() {
  const [topic, setTopic] = useState("");
  const [count, setCount] = useState(5);

  const [roadmap, setRoadmap] = useState([]);
  const [selectedConcept, setSelectedConcept] = useState(null);

  const [papers, setPapers] = useState([]);
  const [papersLoading, setPapersLoading] = useState(false);
  const [papersError, setPapersError] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* ================= ROADMAP ================= */

  const generateRoadmap = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    setError("");
    setRoadmap([]);
    setSelectedConcept(null);
    setPapers([]);
    setPapersError("");

    try {
      const data = await getTopicRoadmap(topic);

      if (!data?.conceptual_path?.length) {
        setError("No conceptual roadmap could be generated for this topic.");
      } else {
        setRoadmap(data.conceptual_path);
      }
    } catch {
      setError("Failed to generate roadmap. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  /* ================= PAPERS ================= */

  const loadPapers = async (concept) => {
    setSelectedConcept(concept);
    setPapers([]);
    setPapersError("");
    setPapersLoading(true);

    try {
      const data = await getTopicPapers(concept, count);

      if (!data.papers_available) {
        setPapers([]);
        setPapersError("Papers not available yet for this topic.");
      } else {
        setPapers(data.papers);
      }
    } catch {
      setPapersError("Failed to fetch papers.");
    } finally {
      setPapersLoading(false);
    }
  };

  return (
    <>
      {/* HEADER */}
      <header className="header">
        <h1>Learning Roadmap</h1>
        <p>First understand the concepts, then study the papers</p>
      </header>

      {/* CONTROLS */}
      <div className="controls-card">
        <input
          className="topic-input"
          placeholder="Enter your research goal "
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />

        <select
          className="count-select"
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
        >
          {[5, 10, 15, 20, 30].map((n) => (
            <option key={n} value={n}>
              {n} papers
            </option>
          ))}
        </select>

        <button
          className="explain-btn"
          onClick={generateRoadmap}
          disabled={loading}
        >
          {loading ? "Building roadmap..." : "Generate Roadmap"}
        </button>
      </div>

      {/* STATUS */}
      {loading && (
        <div className="loading-card">
          Creating conceptual roadmap…
        </div>
      )}

      {!loading && error && (
        <div className="loading-card">
          {error}
        </div>
      )}

      {/* ROADMAP */}
      {!loading && roadmap.length > 0 && (
        <div className="output-area">
          <h3>Conceptual Path to Reach “{topic}”</h3>

          {roadmap.map((c, idx) => (
            <div
              key={idx}
              className={`concept-card ${
                selectedConcept === c.concept ? "active" : ""
              }`}
              onClick={() => loadPapers(c.concept)}
            >
              <h4>{idx + 1}. {c.concept}</h4>
              <p>{c.explanation}</p>
            </div>
          ))}
        </div>
      )}

      {/* PAPERS */}
      {selectedConcept && (
        <div className="output-area">
          <h3>Papers for: {selectedConcept}</h3>

          {papersLoading && (
            <div className="loading-card">
              Fetching papers from arXiv…
            </div>
          )}

          {!papersLoading && papersError && (
            <div className="loading-card">
              {papersError}
            </div>
          )}

          {!papersLoading && !papersError &&
            papers.map((p, i) => (
              <div key={i} className="paper-card">
                <div className="paper-header">
                  <h4>{p.title}</h4>
                  <span className="badge">{p.stage}</span>
                </div>

                <p className="paper-meta">
                  <b>Year:</b> {p.year}
                </p>

                <p><b>Why this paper exists:</b> {p.why_exists}</p>
                <p><b>Read after:</b> {p.read_after}</p>

                <a
                  href={p.link}
                  target="_blank"
                  rel="noreferrer"
                  className="paper-link"
                >
                  Read paper →
                </a>
              </div>
            ))}
        </div>
      )}
    </>
  );
}
