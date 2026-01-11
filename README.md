# 📘 Research Guidance System

**Understand concepts first, then master research papers**

The Research Guidance System is a full-stack application designed to help students and researchers understand research papers **conceptually before diving into technical depth**.  
Instead of plain summarization, the system structures learning through **conceptual roadmaps and multi-level explanations**.

---

## 🎯 Motivation

Most existing paper-explainer tools:
- Dump unstructured text
- Mix equations, figures, and explanations
- Assume strong prior knowledge

This system follows a **learning-first approach**:
1. Understand the concepts
2. Understand the methodology
3. Then understand the technical and mathematical details

---

## 🧠 Key Features

### 1️⃣ Topic Roadmap (Concept-First Learning)
- Generates a conceptual learning path for any research topic
- Explains **why each concept exists**
- Ordered from early ideas → modern approaches
- No equations, no papers, no authors

---

### 2️⃣ Explain Paper (PDF Upload)

Upload a research paper and choose an explanation level:

#### 🟢 Easy
- Beginner-friendly explanation
- No equations
- Focus on problem, motivation, contribution, takeaway

#### 🟡 Intermediate
- Conceptual methodology explanation
- Architecture & flow diagrams extracted from the paper
- A single paragraph explaining what the figures collectively represent
- No mathematical derivations

#### 🔴 Advanced
- Technical methodology explanation
- Equation extraction and explanation
- Bias analysis, metrics, and results interpretation
- Academic tone suitable for research reading

---

## 🏗️ System Architecture

### Backend
- FastAPI-based REST API
- PDF parsing using PyMuPDF (fitz)
- Page-level chunking and semantic role classification
- Regex + semantic fallback extraction
- Figures extracted and aligned with captions
- LLM used only for **explanation**, not blind extraction

### Frontend
- React (Vite)
- Card-based UI
- Level-based explanation views
- Responsive figure grid for architecture diagrams
- Clear separation between text and visuals

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- PyMuPDF
- Groq / OpenAI-compatible LLM API
- feedparser (arXiv integration)

### Frontend
- React
- Vite
- React Markdown
- Custom CSS

---

## 📂 Project Structure
~~~
research-guidance-system/
│
├── backend/
│ ├── main.py
│ ├── uploads/
│ ├── figures/
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ │ ├── EasyView.jsx
│ │ │ ├── IntermediateView.jsx
│ │ │ ├── AdvancedView.jsx
│ │ │ ├── FigureCard.jsx
│ │ │ └── TopicRoadmap.jsx
│ │ ├── api.js
│ │ ├── App.jsx
│ │ └── main.jsx
│ └── package.json
~~~


---

## ▶️ How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload


### Frontend
```bash
cd frontend
npm install
npm run dev

Open the application in your browser at:

http://localhost:5173

