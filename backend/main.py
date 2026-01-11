from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, uuid, re
import fitz
from urllib.parse import quote
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import feedparser
# ================== ENV ==================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env")

# ================== GROQ CLIENT ==================
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ================== APP ==================
app = FastAPI()

# ================== CORS ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== PATHS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FIGURE_DIR = os.path.join(BASE_DIR, "figures")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FIGURE_DIR, exist_ok=True)

app.mount("/figures", StaticFiles(directory=FIGURE_DIR), name="figures")

# ================== UTILS ==================
def clean_pdf_text(text: str) -> str:
    text = re.sub(r"-\n", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def chunk_pdf_by_pages(path: str):
    doc = fitz.open(path)
    chunks = []

    for i, page in enumerate(doc):
        text = clean_pdf_text(page.get_text())
        if len(text) > 200:  # ignore empty pages
            chunks.append({
                "page": i,
                "text": text
            })

    doc.close()
    return chunks

def classify_chunk_role(chunk_text: str) -> str:
    prompt = f"""
Classify the role of the following research paper text.

Possible labels:
BACKGROUND
CORE_IDEA
ARCHITECTURE
MECHANISM
RESULTS
OTHER

Rules:
- Return ONLY ONE label
- No explanation

Text:
{chunk_text[:1500]}
"""
    out = call_llm(prompt).strip().upper()
    allowed = {"BACKGROUND", "CORE_IDEA", "ARCHITECTURE", "MECHANISM", "RESULTS"}
    return out if out in allowed else "OTHER"



def find_methodology_text(full_text: str) -> str:
    patterns = [
        r"iii\.\s*(proposed\s+)?methodology",
        r"3\.\s*(proposed\s+)?methodology",
        r"\bmethodology\b",
        r"\bmethods\b",
        r"\bapproach\b",
        r"\barchitecture\b",
        r"\bframework\b"
    ]
    lower = full_text.lower()
    for pat in patterns:
        m = re.search(pat, lower)
        if m:
            return full_text[m.start():m.start() + 4000]
    return ""

def get_fig_number(caption: str):
    m = re.search(r"fig\.?\s*(\d+)", caption.lower())
    return m.group(1) if m else None

def find_technical_text(full_text: str) -> str:
    patterns = [
        r"iii\.\s*(proposed\s+)?methodology",
        r"3\.\s*(proposed\s+)?methodology",
        r"\bmethodology\b",
        r"\bmethods\b",
        r"\bapproach\b",
        r"\barchitecture\b",
        r"\bframework\b",
        r"\bmodel\s+overview\b",
        r"\bsystem\s+overview\b",
        r"\bproposed\s+system\b",
        r"\bproposed\s+work\b",
        r"\bmodel\s+architecture\b",
        r"\bsystem\s+architecture\b"
    ]

    lower = full_text.lower()
    for pat in patterns:
        m = re.search(pat, lower)
        if m:
            return full_text[m.start():m.start() + 4500]

    return ""

def build_semantic_map(path: str):
    chunks = chunk_pdf_by_pages(path)
    semantic_chunks = []

    for ch in chunks:
        role = classify_chunk_role(ch["text"])
        semantic_chunks.append({
            "page": ch["page"],
            "role": role,
            "text": ch["text"]
        })

    return semantic_chunks

def extract_semantic_technical_text(path: str) -> str:
    semantic_map = build_semantic_map(path)

    selected = [
        ch["text"]
        for ch in semantic_map
        if ch["role"] in {"CORE_IDEA", "ARCHITECTURE", "MECHANISM"}
    ]

    combined = "\n\n".join(selected)
    return combined[:6000]  # safety cap for LLM


# ================== HEALTH ==================
@app.get("/")
def health():
    return {"status": "backend running"}

# ================== UPLOAD ==================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    file_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(path, "wb") as f:
        f.write(await file.read())

    return {"file_id": file_id}

# ================== EASY ==================
@app.post("/explain/easy_llm/{file_id}")
def explain_easy(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "PDF not found")

    doc = fitz.open(path)
    text = clean_pdf_text("".join(p.get_text() for p in doc))
    doc.close()

    def extract(k):
        m = re.search(rf"{k}\b[:\-\—]?", text.lower())
        return text[m.start():m.start() + 2000] if m else ""

    combined = f"""
ABSTRACT:
{extract("abstract")}

INTRODUCTION:
{extract("introduction")}

CONCLUSION:
{extract("conclusion")}
"""

    prompt = f"""
Explain this research paper for a beginner.

Rules:
- Bullet points
- Simple English
- No equations
- Max 8 points

Paper:
{combined}
"""

    return {"level": "easy", "explanation": call_llm(prompt)}

# ================== FIGURES ==================
def extract_figures(path: str):
    doc = fitz.open(path)
    figures, seen = [], set()

    for page_idx, page in enumerate(doc):
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base = doc.extract_image(xref)

            fname = f"fig_p{page_idx}_{img_idx}.png"
            fpath = os.path.join(FIGURE_DIR, fname)

            with open(fpath, "wb") as f:
                f.write(base["image"])

            caption = ""
            for line in page.get_text().split("\n"):
                if re.search(r"\bfig\.?\s*\d+", line.lower()):
                    caption = line.strip()
                    break

            if caption and caption not in seen:
                seen.add(caption)
                figures.append({
                    "image_url": f"/figures/{fname}",
                    "caption": caption
                })

    doc.close()
    return figures

# ================== INTERMEDIATE ==================
@app.post("/explain/intermediate/{file_id}")
def explain_intermediate(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "PDF not found")

    doc = fitz.open(path)
    full_text = clean_pdf_text("".join(p.get_text() for p in doc))
    doc.close()

    # 1️⃣ Technical text extraction
    method_text = find_technical_text(full_text)
    if not method_text:
        method_text = extract_semantic_technical_text(path)

    if not method_text:
        raise HTTPException(500, "Technical content not found")

    # 2️⃣ Extract figures (image + caption ONLY)
    figures = extract_figures(path)

    # 3️⃣ One consolidated explanation for all figures
    figures_summary = ""
    if figures:
        fig_prompt = f"""
The following are figure captions from a research paper.

Task:
Write ONE short paragraph explaining what these diagrams collectively illustrate.

Rules:
- Do NOT explain figures individually
- Do NOT mention figure numbers
- Explain how these diagrams relate to the methodology
- Simple, clear academic English
- 8-10 points maximum and make sure to clearly talk about the displayed images only

Figure captions:
{chr(10).join(f["caption"] for f in figures)}
"""
        figures_summary = call_llm(fig_prompt)

    # 4️⃣ Methodology explanation
    method_prompt = f"""
Explain the methodology conceptually.

Rules:
- Simple English but keep technical meaning
- No equations

Methodology:
{method_text}
"""

    return {
        "level": "intermediate",
        "method_explanation": call_llm(method_prompt),
        "figures": figures,                 # images + captions only
        "figures_summary": figures_summary  # ✅ single paragraph
    }



# ================== ADVANCED ==================
def extract_equations(text: str):
    equations = []
    for line in text.split("\n"):
        if "=" in line and len(line) < 200:
            equations.append(line.strip())
    return list(dict.fromkeys(equations))

def extract_results_text(full_text: str):
    for k in ["results", "evaluation", "performance"]:
        m = re.search(k, full_text.lower())
        if m:
            return full_text[m.start():m.start() + 3500]
    return ""

@app.post("/explain/advanced/{file_id}")
def explain_advanced(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "PDF not found")

    doc = fitz.open(path)
    full_text = clean_pdf_text("".join(p.get_text() for p in doc))
    doc.close()

    # 1️⃣ Technical text with semantic fallback
    technical_text = find_technical_text(full_text)

    if not technical_text:
        technical_text = extract_semantic_technical_text(path)

    if not technical_text:
        raise HTTPException(500, "Technical content not found")

    # 2️⃣ Results section
    results_text = extract_results_text(full_text) or "No results section found."

    # 3️⃣ Methodology explanation
    method_prompt = f"""
Explain the methodology in technical depth.

Rules:
- Write in multiple paragraphs
- Each paragraph should cover one logical component
- No bullet points
- Academic tone

Methodology:
{technical_text}
"""
    methodology_explained = call_llm(method_prompt)

    # 4️⃣ Equation extraction from same semantic scope
    equations = extract_equations(technical_text)
    eq_expl = []

    if equations:
        eq_prompt = f"""
Explain the following equations.

Rules:
- Explain variables
- Explain purpose
- If unclear, say so

Context:
{technical_text}

Equations:
{chr(10).join(equations)}
"""
        eq_expl = call_llm(eq_prompt).split("\n\n")

    # 5️⃣ Results explanation
    res_prompt = f"""
Explain the results.

Rules:
- Explain metrics
- Interpret values
- Mention conclusions

Results:
{results_text}
"""

    return {
        "level": "advanced",
        "methodology_text": methodology_explained,
        "equation_explanations": eq_expl,
        "results_explanation": call_llm(res_prompt)
    }

def generate_conceptual_path(goal: str):
    prompt = f"""
You are an expert ML/NLP researcher guiding a beginner.

Target goal:
{goal}

Task:
List the KEY CONCEPTUAL STEPS that led to the development of this goal.

Focus on:
- Model paradigms
- System-level ideas
- Limitations of earlier approaches
- Concepts that motivated the next evolution

DO NOT include:
- Mathematics (linear algebra, calculus, probability, optimization)
- Programming prerequisites
- Generic academic foundations

Rules:
- Concepts must reflect how the FIELD EVOLVED toward the goal
- Each concept should answer: "Why was this needed?"
- Use terminology commonly used in research literature
- Order concepts from earliest → most recent
- 1–2 line explanation per concept
- Do NOT mention papers or authors
- End the roadmap at the target goal itself

Output format (STRICT):
1. Concept Name | Explanation
2. Concept Name | Explanation
3. Concept Name | Explanation
"""

    output = call_llm(prompt)

    concepts = []
    for line in output.splitlines():
        if "|" in line:
            name, expl = line.split("|", 1)
            concepts.append({
                "concept": name.strip("0123456789. ").strip(),
                "explanation": expl.strip()
            })

    return concepts

class RoadmapRequest(BaseModel):
    topic: str


class PapersRequest(BaseModel):
    concept: str
    count: int = 5



@app.post("/topic/roadmap")
def topic_roadmap(req: RoadmapRequest):
    """
    ONLY generates conceptual roadmap.
    NO arXiv.
    NO feedparser.
    """

    topic = req.topic

    concepts = generate_conceptual_path(topic)

    roadmap = []

    for c in concepts:
        clean_concept = (
            c["concept"]
            .replace("**", "")
            .replace("*", "")
            .replace("`", "")
            .replace("\n", " ")
            .strip()
        )

        roadmap.append({
            "concept": clean_concept,
            "explanation": c["explanation"]
        })

    return {
        "goal": topic,
        "conceptual_path": roadmap
    }


@app.post("/topic/papers")
def topic_papers(req: PapersRequest):
    concept = req.concept
    count = min(req.count, 30)

    clean_concept = (
        concept.replace("**", "")
        .replace("*", "")
        .replace("`", "")
        .replace("\n", " ")
        .strip()
    )

    encoded = quote(clean_concept)

    query = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{encoded}"
        "&start=0&max_results=50"
    )

    feed = feedparser.parse(query)

    if not feed.entries:
        return {
            "concept": clean_concept,
            "papers_available": False,
            "papers": []
        }

    papers = []

    for entry in feed.entries[:count]:
        title = entry.title.replace("\n", " ")
        abstract = entry.summary.replace("\n", " ")
        year = entry.published[:4]

        prompt = f"""
Paper title:
{title}

Paper abstract:
{abstract}

Tasks:
1. Why does this paper exist?
2. Classify as Foundational, Core, or Recent.
3. What should be read before it?

Format:
WHY_EXISTS: ...
STAGE: ...
READ_AFTER: ...
"""

        out = call_llm(prompt)

        why, stage, read_after = "", "", ""

        for line in out.splitlines():
            if line.startswith("WHY_EXISTS:"):
                why = line.replace("WHY_EXISTS:", "").strip()
            elif line.startswith("STAGE:"):
                stage = line.replace("STAGE:", "").strip()
            elif line.startswith("READ_AFTER:"):
                read_after = line.replace("READ_AFTER:", "").strip()

        papers.append({
            "title": title,
            "year": year,
            "link": entry.link,
            "stage": stage or "Core",
            "why_exists": why or "Addresses a gap in prior work.",
            "read_after": read_after or "After understanding foundational concepts."
        })

    return {
        "concept": clean_concept,
        "papers_available": True,
        "papers": papers
    }
