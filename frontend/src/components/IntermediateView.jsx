import ReactMarkdown from "react-markdown";
import FigureCard from "./FigureCard";

export default function IntermediateView({ data }) {
  return (
    <div className="content-card">
      <h2>Methodology (Conceptual Overview)</h2>

      <div className="sub-card">
        <ReactMarkdown>
          {data.method_explanation}
        </ReactMarkdown>
      </div>

      {data.figures && data.figures.length > 0 && (
        <>
          <h3>Architecture & Flow Diagrams</h3>

          <div className="figure-grid">
            {data.figures.map((fig) => (
              <FigureCard key={fig.image_url} fig={fig} />
            ))}
          </div>

          {/* ✅ NEW: single consolidated explanation */}
          {data.figures_summary && (
            <div className="sub-card">
              <p>{data.figures_summary}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
