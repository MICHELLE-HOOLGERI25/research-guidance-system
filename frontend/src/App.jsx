/* 
venv\Scripts\activate
uvicorn main:app --reload
*/
import { useState } from "react";
import {
  uploadPDF,
  explainEasy,
  explainIntermediate,
  explainAdvanced,
} from "./api";

import UploadBox from "./components/UploadBox";
import LevelSelect from "./components/LevelSelect";
import EasyView from "./components/EasyView";
import IntermediateView from "./components/IntermediateView";
import AdvancedView from "./components/AdvancedView";
import TopicRoadmap from "./components/TopicRoadmap";

export default function App() {
  // ✅ Topic Roadmap FIRST
  const [activeTab, setActiveTab] = useState("roadmap");

  // Explain Paper states
  const [fileId, setFileId] = useState(null);
  const [level, setLevel] = useState("easy");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file) => {
    const res = await uploadPDF(file);
    setFileId(res.data.file_id);
    setData(null);
  };

  const loadData = async () => {
    if (!fileId) return;

    setLoading(true);

    const api =
      level === "easy"
        ? explainEasy
        : level === "intermediate"
        ? explainIntermediate
        : explainAdvanced;

    try {
      const res = await api(fileId);
      setData({ level, payload: res.data });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="workspace">

        {/* ===== COMMON HEADER ===== */}
        <header className="header">
          <h1>Research Guidance System</h1>
          <p>Understand concepts first, then master research papers</p>
        </header>

        {/* ===== CENTERED TABS (ROADMAP FIRST) ===== */}
        <div className="tabs center-tabs">
          <button
            className={activeTab === "roadmap" ? "active" : ""}
            onClick={() => setActiveTab("roadmap")}
          >
            Topic Roadmap
          </button>

          <button
            className={activeTab === "explain" ? "active" : ""}
            onClick={() => setActiveTab("explain")}
          >
            Explain Paper
          </button>
        </div>

        {/* ===== TAB CONTENT ===== */}
        {activeTab === "roadmap" && <TopicRoadmap />}

        {activeTab === "explain" && (
          <>
            <div className="controls-card wide">
              <UploadBox onUpload={handleUpload} />
              <LevelSelect level={level} setLevel={setLevel} />

              <button
                className="explain-btn"
                onClick={loadData}
                disabled={!fileId || loading}
              >
                {loading ? "Explaining..." : "Explain"}
              </button>
            </div>

            <div className="output-area">
              {loading && (
                <div className="loading-card">
                  Generating explanation…
                </div>
              )}

              {!loading && data?.level === "easy" && (
                <EasyView data={data.payload} />
              )}

              {!loading && data?.level === "intermediate" && (
                <IntermediateView data={data.payload} />
              )}

              {!loading && data?.level === "advanced" && (
                <AdvancedView data={data.payload} />
              )}
            </div>
          </>
        )}

      </div>
    </div>
  );
}
