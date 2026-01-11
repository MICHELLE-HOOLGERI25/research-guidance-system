export default function LevelSelect({ level, setLevel }) {
  return (
    <select
      value={level}
      onChange={(e) => setLevel(e.target.value)}
      className="level-select"
    >
      <option value="easy">Easy</option>
      <option value="intermediate">Intermediate</option>
      <option value="advanced">Advanced</option>
    </select>
  );
}
