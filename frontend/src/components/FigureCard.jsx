export default function FigureCard({ fig }) {

  const cleanText = (text = "") => {
    let t = text;

    // ❌ Remove generic LLM prefaces
    t = t.replace(/here are the explanations.*?:/i, "");
    t = t.replace(/i'?ll explain each figure.*?:?/i, "");
    t = t.replace(/i'?d be happy to explain.*?:?/i, "");

    // ❌ Remove LLM disclaimers
    t = t.replace(/i do not have (direct )?access.*$/i, "");

    // ❌ Remove repeated figure references
    t = t.replace(/fig\.?\s*\d+[:.\-\s]*/gi, "");

    // ❌ Remove markdown noise
    t = t.replace(/\*\*/g, "").trim();

    // ❌ If explanation is too small → useless
    if (t.length < 25) return null;

    return t;
  };

  const explanation = cleanText(fig.explanation);

  return (
    <div className="figure-card">
      <div className="figure-img-box">
        <img
          src={`http://127.0.0.1:8000${fig.image_url}`}
          alt={fig.caption}
        />
      </div>

      <h4>{fig.caption}</h4>

      {fig.explanation && <p>{fig.explanation}</p>}
    </div>
  );
}
