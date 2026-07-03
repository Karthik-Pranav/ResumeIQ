
# ResumeIQ

An AI-powered resume analyzer that compares a candidate's resume against a job description and returns a semantic match score, detected strengths, skill gaps, and the most relevant resume sections.

---

## Problem Statement

Traditional resume screening tools rely on keyword frequency or simple string matching. These approaches fail in common situations — a resume that says "built ML pipelines" won't match a JD that asks for "machine learning experience", even though they mean the same thing. They also struggle when the job description itself is vague (e.g., "AI developer").

ResumeIQ addresses this by using sentence-level embeddings to compare meaning rather than words, and by intelligently expanding vague job descriptions before analysis.

---

## Approach

### Core Idea

The system treats both the resume and job description as semantic documents rather than keyword bags. It uses a sentence-transformer model to generate vector representations and compares them using cosine similarity.

### Pipeline

```
Resume PDF  ──► PDF Parser ──► Plain Text
                                   │
Job Description ──► JD Expander ──► Expanded JD
                                   │
                          Embedding Model (all-MiniLM-L6-v2)
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
             Overall Score                 Chunk Matching
          (resume vs full JD)         (top-3 section pairs)
                                             │
                              Keyword Extractor (phrase whitelist)
                                             │
                              Semantic Matcher (skill-by-skill)
                                             │
                              Strengths / Gaps (threshold: 0.45)
```

### Key Decisions

The design focuses on semantic understanding, explainability, and robustness to poor inputs.

**Sentence Transformers over TF-IDF or BM25**
TF-IDF scores term frequency; it has no understanding of synonyms or context. `all-MiniLM-L6-v2` produces 384-dimensional embeddings trained on semantic similarity tasks, making it well-suited for resume-to-JD comparison without requiring a large model or API calls.

**Chunk-based matching over full-document comparison**
Embedding an entire resume as a single vector loses structural information. Splitting the resume into chunks and comparing them against JD segments helps surface which sections are most relevant.

**JD Expansion for vague inputs**
Short job descriptions produce weak embeddings. The system detects this case and expands the JD using a curated role-to-skills mapping (e.g., "AI developer" → machine learning, NLP, Python, deployment). Expansion is capped to avoid noise and is shown transparently to the user.

**Embedding-based skill matching over exact string search**
Instead of checking for exact keyword matches, each skill is embedded and compared against resume sentences. A skill is considered present if similarity exceeds a configurable threshold (default: 0.45).

**Structured keyword extraction via phrase whitelist**
A curated dictionary of 150+ tech terms maps skills into `core_skills`, `tools`, and `concepts`, preventing generic words like "developer" from appearing as gaps.

---

## Architecture Overview

```
ResumeIQ/
├── app/
│   ├── main.py                    FastAPI entrypoint
│   ├── routers/
│   │   └── analysis_router.py    POST /analyze endpoint
│   ├── services/
│   │   └── analysis_service.py   Core orchestration
│   ├── models/
│   │   └── schemas.py            Pydantic models
│   └── utils/
│       ├── pdf_parser.py
│       ├── chunker.py
│       ├── embedding.py
│       ├── similarity.py
│       ├── jd_expander.py
│       ├── keyword_extractor.py
│       ├── semantic_matcher.py
│       └── keyword_analysis.py
│
└── frontend/
    └── src/
        ├── components/
        │   └── ResumeAnalyzer.tsx
        └── types/
            └── api.ts
```

---

## Features

* Semantic match score (0–100)
* Strengths detection using semantic similarity
* Gap detection for missing skills
* Top-3 matched resume sections
* JD expansion for vague inputs
* Structured keyword breakdown (skills, tools, concepts)
* Configurable similarity threshold via `.env`
* PDF validation and error handling

---

## Limitations

* Skill mapping is rule-based and may not cover niche roles
* No real-time job market or dynamic skill taxonomy
* Semantic similarity may miss highly domain-specific nuances

These can be improved using structured taxonomies or LLM-based expansion.

---

## Tech Stack

| Layer       | Technology       | Purpose                 |
| ----------- | ---------------- | ----------------------- |
| Backend     | FastAPI          | API framework           |
| ML Model    | all-MiniLM-L6-v2 | Semantic embeddings     |
| PDF Parsing | PyMuPDF          | Resume text extraction  |
| Computation | NumPy            | Similarity calculations |
| Frontend    | Next.js          | UI                      |
| HTTP Client | Axios            | API calls               |
| Validation  | Pydantic         | Data validation         |
| Styling     | Tailwind CSS     | UI styling              |

---

## Setup Instructions

### Backend

```bash
git clone https://github.com/your-username/ResumeIQ.git
cd ResumeIQ

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Example Output

```json
{
  "match_score": 64,
  "matched_role": "ai developer",
  "strengths": ["Python", "Machine Learning"],
  "gaps": ["Deep Learning", "NLP", "PyTorch"],
  "matched_sections": [...]
}
```

---

## Reflection

When I first approached this problem, I considered using a large language model. However, I chose sentence-transformers due to lower latency, zero API cost, and strong performance on semantic similarity tasks.

The biggest challenge was improving keyword extraction and skill matching. A simple regex-based approach produced poor results, especially for vague inputs. I replaced this with a phrase-whitelist system combined with embedding-based matching, which significantly improved output quality.

Handling vague job descriptions was another challenge. Instead of returning weak results, the system detects short inputs and expands them using a predefined skill mapping. This improves accuracy while maintaining transparency.

One deliberate trade-off was using a static skill map instead of a generative approach. While less flexible, it ensures deterministic, explainable outputs without introducing external dependencies.

During testing, I noticed that the system still struggles with loosely structured or informal job descriptions. For example, inputs like "web developer, with experience in mongodb, next.js, express, and react preferably some ai skills as well" can lead to noisy keyword extraction, where non-skill tokens such as "preferably" or "well" are incorrectly treated as skills. This happens because the current keyword extraction pipeline, while improved with a phrase whitelist, still allows residual tokens when the input is not cleanly structured.

Another limitation is normalization. Variations like "React" vs "React.js" or "Next.js" vs "Next.js 15" are not fully unified, which can cause valid skills to appear as gaps. Similarly, the semantic matching threshold can sometimes be too strict for borderline matches, especially when phrasing differs.

These issues highlight that while the core embedding-based approach is strong, the preprocessing and normalization layers are equally important for producing clean, reliable outputs. With more time, I would improve this by adding stricter filtering, better normalization rules, and potentially a lightweight parsing step to clean user input before analysis.

