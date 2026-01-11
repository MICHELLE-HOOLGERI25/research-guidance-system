import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

/* ===== PDF EXPLAIN ===== */

export const uploadPDF = (file) => {
  const form = new FormData();
  form.append("file", file);
  return API.post("/upload", form);
};

export const explainEasy = (id) =>
  API.post(`/explain/easy_llm/${id}`);

export const explainIntermediate = (id) =>
  API.post(`/explain/intermediate/${id}`);

export const explainAdvanced = (id) =>
  API.post(`/explain/advanced/${id}`);

/* ===== TOPIC ROADMAP ===== */

export const getTopicRoadmap = async (topic) => {
  const res = await API.post("/topic/roadmap", { topic });
  return res.data;
};

export const getTopicPapers = async (concept, count) => {
  const res = await API.post("/topic/papers", {
    concept,
    count,
  });
  return res.data;
};
