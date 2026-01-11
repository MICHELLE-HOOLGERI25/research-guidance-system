export default function LevelTabs({ level, setLevel }) {
  return (
    <div className="tabs">
      {["easy", "intermediate", "advanced"].map(l => (
        <button
          key={l}
          className={level === l ? "active" : ""}
          onClick={() => setLevel(l)}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
