import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function EasyView({ data }) {
  return (
    <div className="content-card">
      <h3>Paper Summary</h3>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {data.explanation}
      </ReactMarkdown>
    </div>
  );
}
