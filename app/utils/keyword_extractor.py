"""Structured keyword extraction from job descriptions.

Replaces the old regex/stopword approach with a two-pass strategy:

Pass 1 — Phrase whitelist
    Check the JD against a curated dictionary of 150+ tech terms mapped to
    one of three categories: core_skills, tools, concepts.
    Longer phrases are checked first so "machine learning" isn't split into
    two single tokens.

Pass 2 — Residual single-token sweep
    Remaining non-whitelist words are filtered through an extended "filler"
    set that removes generic nouns like "developer", "engineer", "role", etc.
    Surviving tokens are classified as "core_skills" (default bucket).

Output — ExtractedKeywords dataclass
    Exposes core_skills, tools, concepts lists and an all_skills() helper
    for downstream embedding lookup.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Extended filler words (not shown to users as gaps/strengths) ──────────────
# Combines the old STOPWORDS with job-posting generic nouns that aren't skills.
FILLER_WORDS: frozenset[str] = frozenset(
    {
        # Standard stopwords
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "as", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "shall", "should", "may", "might", "must", "can",
        "could", "about", "above", "after", "all", "also", "am", "any",
        "because", "before", "between", "both", "during", "each", "few",
        "further", "get", "got", "he", "her", "here", "him", "his",
        "how", "i", "into", "it", "its", "just", "me", "more", "most", "my",
        "no", "nor", "not", "now", "only", "other", "our", "out", "own",
        "same", "she", "so", "some", "such", "than", "that", "their", "them",
        "then", "there", "these", "they", "this", "those", "through", "too",
        "under", "until", "up", "us", "very", "we", "what", "when", "where",
        "which", "while", "who", "whom", "why", "you", "your",
        # Generic job-posting nouns — these are NOT skills
        "developer", "engineer", "development", "engineering", "role", "job",
        "position", "team", "company", "candidate", "applicant", "hire",
        "hiring", "joining", "join", "opportunity", "experience", "background",
        "qualifications", "requirements", "responsibilities", "duties",
        "skills", "skill", "knowledge", "understanding", "ability", "able",
        "proficiency", "proficient", "expertise", "expert", "strong",
        "excellent", "good", "great", "best", "high", "new", "looking",
        "minimum", "preferred", "required", "plus", "etc", "eg", "ie",
        "year", "years", "month", "months", "work", "working", "build",
        "building", "design", "designing", "develop", "developing",
        "implement", "implementing", "maintain", "maintaining", "support",
        "supporting", "deliver", "delivering", "ensure", "ensuring",
        "collaborate", "collaborating", "manage", "managing", "lead",
        "leading", "within", "across", "including", "using", "using",
        "basis", "level", "levels", "type", "types", "area", "areas",
        "field", "fields", "space", "sector", "industry",
    }
)

# ── Phrase whitelist: phrase → (category, canonical display name) ─────────────
# Longer phrases MUST come before shorter overlapping ones — dict is ordered.
# category: "core_skills" | "tools" | "concepts"
PHRASE_WHITELIST: dict[str, tuple[str, str]] = {
    # ── AI / ML / Data ───────────────────────────────────────────────────────
    "natural language processing": ("core_skills", "natural language processing"),
    "large language models":       ("concepts",    "large language models"),
    "large language model":        ("concepts",    "large language models"),
    "reinforcement learning":      ("concepts",    "reinforcement learning"),
    "transfer learning":           ("concepts",    "transfer learning"),
    "computer vision":             ("core_skills", "computer vision"),
    "object detection":            ("core_skills", "object detection"),
    "image segmentation":          ("concepts",    "image segmentation"),
    "machine learning":            ("core_skills", "machine learning"),
    "deep learning":               ("core_skills", "deep learning"),
    "model deployment":            ("core_skills", "model deployment"),
    "model training":              ("core_skills", "model training"),
    "feature engineering":         ("concepts",    "feature engineering"),
    "data preprocessing":          ("concepts",    "data preprocessing"),
    "data pipeline":               ("core_skills", "data pipelines"),
    "data pipelines":              ("core_skills", "data pipelines"),
    "data analysis":               ("core_skills", "data analysis"),
    "data visualization":          ("core_skills", "data visualization"),
    "data science":                ("core_skills", "data science"),
    "data engineering":            ("core_skills", "data engineering"),
    "data warehouse":              ("concepts",    "data warehouse"),
    "data lake":                   ("concepts",    "data lake"),
    "statistical modeling":        ("concepts",    "statistical modeling"),
    "a/b testing":                 ("concepts",    "a/b testing"),
    "hypothesis testing":          ("concepts",    "hypothesis testing"),
    "neural network":              ("concepts",    "neural networks"),
    "neural networks":             ("concepts",    "neural networks"),
    "convolutional neural":        ("concepts",    "convolutional neural networks"),
    "hyperparameter tuning":       ("concepts",    "hyperparameter tuning"),
    "sentiment analysis":          ("concepts",    "sentiment analysis"),
    "text classification":         ("core_skills", "text classification"),
    "named entity recognition":    ("core_skills", "named entity recognition"),
    "information retrieval":       ("concepts",    "information retrieval"),
    "generative ai":               ("concepts",    "generative ai"),
    "prompt engineering":          ("concepts",    "prompt engineering"),
    # ── AI / ML Tools ────────────────────────────────────────────────────────
    "hugging face":    ("tools", "hugging face"),
    "scikit-learn":    ("tools", "scikit-learn"),
    "scikit learn":    ("tools", "scikit-learn"),
    "tensorflow":      ("tools", "tensorflow"),
    "pytorch":         ("tools", "pytorch"),
    "keras":           ("tools", "keras"),
    "xgboost":         ("tools", "xgboost"),
    "lightgbm":        ("tools", "lightgbm"),
    "spacy":           ("tools", "spacy"),
    "nltk":            ("tools", "nltk"),
    "transformers":    ("tools", "transformers"),
    "langchain":       ("tools", "langchain"),
    "openai":          ("tools", "openai api"),
    "mlflow":          ("tools", "mlflow"),
    "weights & biases":("tools", "weights & biases"),
    # ── Languages ────────────────────────────────────────────────────────────
    "python":      ("core_skills", "python"),
    "javascript":  ("core_skills", "javascript"),
    "typescript":  ("core_skills", "typescript"),
    "java":        ("core_skills", "java"),
    "golang":      ("core_skills", "golang"),
    "rust":        ("core_skills", "rust"),
    "scala":       ("core_skills", "scala"),
    "kotlin":      ("core_skills", "kotlin"),
    "swift":       ("core_skills", "swift"),
    "ruby":        ("core_skills", "ruby"),
    "php":         ("core_skills", "php"),
    "c++":         ("core_skills", "c++"),
    "c#":          ("core_skills", "c#"),
    "r":           ("core_skills", "r"),
    "bash":        ("tools",       "bash"),
    "shell":       ("tools",       "shell scripting"),
    "matlab":      ("tools",       "matlab"),
    # ── Web / Backend ────────────────────────────────────────────────────────
    "restful api":          ("core_skills", "rest api"),
    "rest api":             ("core_skills", "rest api"),
    "rest apis":            ("core_skills", "rest api"),
    "graphql":              ("tools",       "graphql"),
    "microservices":        ("concepts",    "microservices"),
    "microservices architecture": ("concepts", "microservices architecture"),
    "system design":        ("concepts",    "system design"),
    "software engineering": ("core_skills", "software engineering"),
    "software development": ("core_skills", "software development"),
    "object oriented":      ("concepts",    "object oriented programming"),
    "object-oriented":      ("concepts",    "object oriented programming"),
    "design patterns":      ("concepts",    "design patterns"),
    "domain driven design": ("concepts",    "domain driven design"),
    "fastapi":    ("tools", "fastapi"),
    "django":     ("tools", "django"),
    "flask":      ("tools", "flask"),
    "express":    ("tools", "express.js"),
    "node.js":    ("tools", "node.js"),
    "nodejs":     ("tools", "node.js"),
    "spring":     ("tools", "spring boot"),
    "rails":      ("tools", "ruby on rails"),
    "next.js":    ("tools", "next.js"),
    "react":      ("tools", "react"),
    "angular":    ("tools", "angular"),
    "vue":        ("tools", "vue.js"),
    "tailwind":   ("tools", "tailwind css"),
    "html":       ("core_skills", "html"),
    "css":        ("core_skills", "css"),
    # ── Databases ────────────────────────────────────────────────────────────
    "sql":          ("core_skills", "sql"),
    "postgresql":   ("tools", "postgresql"),
    "postgres":     ("tools", "postgresql"),
    "mysql":        ("tools", "mysql"),
    "mongodb":      ("tools", "mongodb"),
    "redis":        ("tools", "redis"),
    "elasticsearch":("tools", "elasticsearch"),
    "cassandra":    ("tools", "cassandra"),
    "bigquery":     ("tools", "bigquery"),
    "snowflake":    ("tools", "snowflake"),
    # ── Cloud / DevOps ────────────────────────────────────────────────────────
    "amazon web services": ("tools",    "aws"),
    "google cloud platform":("tools",   "gcp"),
    "google cloud":         ("tools",   "gcp"),
    "microsoft azure":      ("tools",   "azure"),
    "kubernetes":           ("tools",   "kubernetes"),
    "docker":               ("tools",   "docker"),
    "terraform":            ("tools",   "terraform"),
    "ansible":              ("tools",   "ansible"),
    "github actions":       ("tools",   "github actions"),
    "jenkins":              ("tools",   "jenkins"),
    "prometheus":           ("tools",   "prometheus"),
    "grafana":              ("tools",   "grafana"),
    "infrastructure as code":("concepts","infrastructure as code"),
    "ci/cd":                ("concepts","ci/cd"),
    "ci cd":                ("concepts","ci/cd"),
    "devops":               ("concepts","devops"),
    "containerization":     ("concepts","containerization"),
    "serverless":           ("concepts","serverless"),
    "linux":                ("tools",   "linux"),
    "unix":                 ("tools",   "unix"),
    "aws":                  ("tools",   "aws"),
    "gcp":                  ("tools",   "gcp"),
    "azure":                ("tools",   "azure"),
    # ── Data Engineering ─────────────────────────────────────────────────────
    "apache spark":  ("tools", "apache spark"),
    "spark":         ("tools", "apache spark"),
    "airflow":       ("tools", "apache airflow"),
    "kafka":         ("tools", "apache kafka"),
    "dbt":           ("tools", "dbt"),
    "hadoop":        ("tools", "hadoop"),
    "hive":          ("tools", "hive"),
    "pandas":        ("tools", "pandas"),
    "numpy":         ("tools", "numpy"),
    "etl":           ("concepts", "etl"),
    "batch processing":  ("concepts","batch processing"),
    "stream processing": ("concepts","stream processing"),
    "distributed computing":("concepts","distributed computing"),
    # ── General engineering ───────────────────────────────────────────────────
    "git":              ("tools",    "git"),
    "version control":  ("concepts", "version control"),
    "code review":      ("concepts", "code review"),
    "unit testing":     ("concepts", "unit testing"),
    "integration testing":("concepts","integration testing"),
    "test driven":      ("concepts", "test driven development"),
    "agile":            ("concepts", "agile"),
    "scrum":            ("concepts", "scrum"),
    "algorithms":       ("core_skills","algorithms"),
    "data structures":  ("core_skills","data structures"),
    "problem solving":  ("concepts",   "problem solving"),
    "authentication":   ("concepts",   "authentication"),
    "security":         ("concepts",   "security"),
    "performance optimization":("concepts","performance optimization"),
    "scalability":      ("concepts", "scalability"),
    "high availability":("concepts", "high availability"),
    "caching":          ("concepts", "caching"),
    "nlp":              ("core_skills", "nlp"),
    "llm":              ("concepts",    "large language models"),
    "llms":             ("concepts",    "large language models"),
    "embeddings":       ("concepts",    "embeddings"),
    "vector database":  ("tools",       "vector database"),
    "rag":              ("concepts",    "retrieval augmented generation"),
}

# Pre-sort by descending phrase length so longer phrases are matched first
_SORTED_PHRASES: list[tuple[str, tuple[str, str]]] = sorted(
    PHRASE_WHITELIST.items(), key=lambda kv: len(kv[0]), reverse=True
)


# ── Output dataclass ──────────────────────────────────────────────────────────

@dataclass
class ExtractedKeywords:
    """Structured keywords extracted from a job description."""

    core_skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)

    def all_skills(self) -> list[str]:
        """Return a flat deduplicated list of all extracted skills."""
        seen: set[str] = set()
        combined: list[str] = []
        for skill in self.core_skills + self.tools + self.concepts:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                combined.append(skill)
        return combined

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "core_skills": self.core_skills,
            "tools": self.tools,
            "concepts": self.concepts,
        }


# ── Public API ────────────────────────────────────────────────────────────────

def extract_keywords(job_description: str) -> ExtractedKeywords:
    """Extract structured keywords from *job_description*.

    Args:
        job_description: The (possibly already expanded) JD text.

    Returns:
        An ExtractedKeywords instance.
    """
    jd_lower = job_description.lower()
    result = ExtractedKeywords()

    seen_canonical: set[str] = set()
    consumed_spans: list[tuple[int, int]] = []

    # ── Pass 1: phrase whitelist ──────────────────────────────────────────────
    for phrase, (category, canonical) in _SORTED_PHRASES:
        if canonical.lower() in seen_canonical:
            continue
        start = 0
        while True:
            idx = jd_lower.find(phrase, start)
            if idx == -1:
                break
            end = idx + len(phrase)
            # Check word boundaries (don't match mid-word)
            before_ok = idx == 0 or not jd_lower[idx - 1].isalpha()
            after_ok = end == len(jd_lower) or not jd_lower[end].isalpha()
            if before_ok and after_ok:
                if not _overlaps(idx, end, consumed_spans):
                    canonical_lower = canonical.lower()
                    if canonical_lower not in seen_canonical:
                        seen_canonical.add(canonical_lower)
                        consumed_spans.append((idx, end))
                        _add_to(result, category, canonical)
                break
            start = end

    # ── Pass 2: residual single-token sweep ───────────────────────────────────
    # Replace consumed regions with spaces so their tokens aren't re-extracted
    jd_residual = list(jd_lower)
    for s, e in consumed_spans:
        for i in range(s, e):
            jd_residual[i] = " "
    residual_text = "".join(jd_residual)

    tokens = re.findall(r"[a-z][a-z0-9#+.'/-]*", residual_text)
    for token in tokens:
        if token in FILLER_WORDS or len(token) <= 1:
            continue
        if token in seen_canonical:
            continue
        # Check if this single token appears in the whitelist as a key
        if token in PHRASE_WHITELIST:
            cat, canonical = PHRASE_WHITELIST[token]
            if canonical.lower() not in seen_canonical:
                seen_canonical.add(canonical.lower())
                _add_to(result, cat, canonical)
        else:
            # Unknown token — add to core_skills only if it looks technical
            # (at least 3 chars, not purely numeric, not a filler)
            if len(token) >= 3 and not token.isdigit():
                seen_canonical.add(token)
                result.core_skills.append(token)

    return result


# ── Private helpers ───────────────────────────────────────────────────────────

def _overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    """Return True if [start, end) overlaps any existing consumed span."""
    for s, e in spans:
        if not (end <= s or start >= e):
            return True
    return False


def _add_to(result: ExtractedKeywords, category: str, canonical: str) -> None:
    """Append *canonical* to the correct list in *result*."""
    if category == "core_skills":
        result.core_skills.append(canonical)
    elif category == "tools":
        result.tools.append(canonical)
    else:
        result.concepts.append(canonical)
