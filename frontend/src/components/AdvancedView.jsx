import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function AdvancedView({ data }) {
  return (
    <div className="content-card">
      <h3>Methodology (Technical)</h3>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {data.methodology_text}
      </ReactMarkdown>

      <h3>Equation Explanation</h3>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {data.equation_explanations.join("\n\n")}
      </ReactMarkdown>

      <h3>Results & Evaluation</h3>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {data.results_explanation}
      </ReactMarkdown>
    </div>
  );
}
