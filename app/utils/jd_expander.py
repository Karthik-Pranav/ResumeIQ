"""Job description expansion for weak/vague JD inputs.

Detects short or vague job descriptions (fewer than WEAK_JD_WORD_THRESHOLD
meaningful tokens) and replaces them with a richer skill-cluster derived
from a curated role → skills mapping.

Design decisions
----------------
* Pure stdlib + a small hand-crafted lookup table — no external API calls.
* Role matching uses token-overlap so "senior AI developer" still hits
  the "ai developer" entry even with the prefix word.
* Expansion is capped at MAX_EXPANSION_SKILLS (8) to avoid flooding the
  downstream keyword extractor with noise.
* The original JD text is always preserved alongside the expansion so the
  overall semantics don't flip — we *augment*, not replace.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Tuneable constants ────────────────────────────────────────────────────────

# Fewer *meaningful* words than this → JD is considered weak.
WEAK_JD_WORD_THRESHOLD: int = 5

# Hard cap on how many expanded skills are appended to the JD text.
MAX_EXPANSION_SKILLS: int = 8

# ── Stopwords (shared minimal set — just for word-count purposes) ─────────────
_COUNT_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "as", "is", "are", "was", "were",
        "be", "been", "will", "would", "can", "could", "must", "should",
        "may", "might", "we", "our", "you", "your", "i", "am", "this",
        "that", "about", "who", "what", "how", "very", "also", "both",
        "need", "needs", "looking", "seeking", "hire", "hiring",
    }
)

# ── Role → skill-cluster map ──────────────────────────────────────────────────
# Keys: canonical lowercase role aliases (comma-separated variants in list).
# Values: dict with core_skills / tools / concepts lists.
# All three lists combined must not exceed MAX_EXPANSION_SKILLS total — the
# expander will slice to that cap after combining anyway.

_RAW_ROLE_MAP: list[tuple[list[str], dict[str, list[str]]]] = [
    (
        ["ai developer", "ai engineer", "artificial intelligence developer",
         "artificial intelligence engineer"],
        {
            "core_skills": ["machine learning", "deep learning", "nlp", "python",
                            "model training", "model deployment"],
            "tools":       ["tensorflow", "pytorch", "scikit-learn"],
            "concepts":    ["neural networks", "transfer learning",
                            "data preprocessing", "feature engineering"],
        },
    ),
    (
        ["ml engineer", "machine learning engineer", "ml developer"],
        {
            "core_skills": ["machine learning", "python", "model deployment",
                            "feature engineering", "statistical modeling"],
            "tools":       ["scikit-learn", "pandas", "mlflow", "docker"],
            "concepts":    ["supervised learning", "unsupervised learning",
                            "cross-validation", "hyperparameter tuning"],
        },
    ),
    (
        ["data scientist", "data science"],
        {
            "core_skills": ["machine learning", "python", "data analysis",
                            "statistical modeling", "data visualization"],
            "tools":       ["pandas", "numpy", "matplotlib", "scikit-learn", "sql"],
            "concepts":    ["hypothesis testing", "regression", "clustering",
                            "a/b testing"],
        },
    ),
    (
        ["data engineer", "data pipeline engineer"],
        {
            "core_skills": ["etl", "data pipelines", "sql", "python",
                            "distributed computing"],
            "tools":       ["apache spark", "airflow", "kafka", "dbt",
                            "amazon s3", "bigquery"],
            "concepts":    ["data warehouse", "data lake", "batch processing",
                            "stream processing"],
        },
    ),
    (
        ["backend developer", "backend engineer", "server-side developer",
         "api developer", "api engineer"],
        {
            "core_skills": ["rest api", "python", "sql", "system design",
                            "microservices"],
            "tools":       ["fastapi", "django", "flask", "postgresql",
                            "redis", "docker"],
            "concepts":    ["authentication", "caching", "database design",
                            "ci/cd"],
        },
    ),
    (
        ["frontend developer", "frontend engineer", "ui developer",
         "react developer", "next.js developer"],
        {
            "core_skills": ["javascript", "react", "html", "css",
                            "responsive design"],
            "tools":       ["typescript", "next.js", "tailwind css", "webpack",
                            "git"],
            "concepts":    ["component architecture", "state management",
                            "accessibility", "performance optimization"],
        },
    ),
    (
        ["fullstack developer", "full stack developer", "full-stack developer",
         "fullstack engineer", "full stack engineer"],
        {
            "core_skills": ["javascript", "python", "rest api", "react", "sql"],
            "tools":       ["node.js", "fastapi", "postgresql", "docker", "git"],
            "concepts":    ["microservices", "authentication", "ci/cd",
                            "responsive design"],
        },
    ),
    (
        ["devops engineer", "devops developer", "platform engineer",
         "site reliability engineer", "sre"],
        {
            "core_skills": ["ci/cd", "infrastructure as code", "linux",
                            "kubernetes", "docker"],
            "tools":       ["terraform", "ansible", "github actions", "jenkins",
                            "prometheus"],
            "concepts":    ["monitoring", "scalability", "incident management",
                            "containerization"],
        },
    ),
    (
        ["cloud engineer", "cloud architect", "cloud developer",
         "aws engineer", "gcp engineer", "azure engineer"],
        {
            "core_skills": ["cloud infrastructure", "networking",
                            "security", "infrastructure as code", "linux"],
            "tools":       ["amazon web services", "google cloud platform",
                            "microsoft azure", "terraform", "kubernetes"],
            "concepts":    ["high availability", "disaster recovery",
                            "cost optimization", "scalability"],
        },
    ),
    (
        ["software engineer", "software developer", "software development",
         "programmer", "developer"],
        {
            "core_skills": ["python", "algorithms", "data structures",
                            "system design", "rest api"],
            "tools":       ["git", "docker", "sql", "linux"],
            "concepts":    ["object oriented programming", "design patterns",
                            "code review", "testing"],
        },
    ),
    (
        ["nlp engineer", "nlp developer", "natural language processing engineer"],
        {
            "core_skills": ["nlp", "python", "text classification",
                            "named entity recognition", "machine learning"],
            "tools":       ["hugging face", "spacy", "nltk", "transformers",
                            "pytorch"],
            "concepts":    ["tokenization", "embeddings", "language models",
                            "sequence modeling"],
        },
    ),
    (
        ["computer vision engineer", "cv engineer", "vision developer"],
        {
            "core_skills": ["computer vision", "python", "image processing",
                            "deep learning", "object detection"],
            "tools":       ["opencv", "pytorch", "tensorflow", "yolo"],
            "concepts":    ["convolutional neural networks", "image segmentation",
                            "feature extraction", "model inference"],
        },
    ),
]

# Build a flat dict: canonical_key → skill_dict
ROLE_SKILL_MAP: dict[str, dict[str, list[str]]] = {}
for _aliases, _skills in _RAW_ROLE_MAP:
    for _alias in _aliases:
        ROLE_SKILL_MAP[_alias] = _skills


# ── Public API ────────────────────────────────────────────────────────────────

@dataclass
class JDExpansionResult:
    """Result of the JD expansion step."""

    expanded_jd: str
    """The (possibly augmented) job description to use for downstream analysis."""

    was_expanded: bool
    """True when the original JD was detected as weak and expanded."""

    matched_role: str | None
    """The canonical role name matched, or None if no match / not expanded."""

    warning: str | None
    """Human-readable note to surface in the UI, or None."""


def expand_jd(job_description: str) -> JDExpansionResult:
    """Detect a weak JD and enrich it with role-derived skills.

    Args:
        job_description: Raw job description text from the user.

    Returns:
        A JDExpansionResult.  If the JD is already detailed,
        ``was_expanded`` will be False and ``expanded_jd`` equals
        the original text (stripped).
    """
    jd = job_description.strip()
    meaningful_count = _count_meaningful_words(jd)

    if meaningful_count >= WEAK_JD_WORD_THRESHOLD:
        # Detailed enough — pass through unchanged
        return JDExpansionResult(
            expanded_jd=jd,
            was_expanded=False,
            matched_role=None,
            warning=None,
        )

    # JD is short/vague — try to match a role
    canonical_role, skill_dict = _match_role(jd)

    if skill_dict is None:
        # No role match; warn the user but still pass the original through
        return JDExpansionResult(
            expanded_jd=jd,
            was_expanded=False,
            matched_role=None,
            warning=(
                "The job description is very short. "
                "Consider adding more detail for a better match score."
            ),
        )

    # Build the expansion string from capped skill list
    all_skills = _flatten_skills(skill_dict)
    expansion = ", ".join(all_skills)
    expanded_jd = f"{jd}. Skills and expertise: {expansion}."

    warning = (
        f"Short job description detected. "
        f"Automatically expanded using the '{canonical_role}' role profile "
        f"({len(all_skills)} skills added)."
    )

    return JDExpansionResult(
        expanded_jd=expanded_jd,
        was_expanded=True,
        matched_role=canonical_role,
        warning=warning,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _count_meaningful_words(text: str) -> int:
    """Return the number of non-stopword tokens in *text*."""
    tokens = re.findall(r"[a-z][a-z0-9#.+/'-]*", text.lower())
    return sum(1 for t in tokens if t not in _COUNT_STOPWORDS)


def _match_role(
    jd: str,
) -> tuple[str, dict[str, list[str]]] | tuple[None, None]:
    """Attempt to match *jd* against the role-synonym map.

    Matching strategy:
    1. Exact substring match (fastest, covers "ai developer" in "senior ai developer").
    2. Token-overlap: if at least 2 tokens from the role alias appear in the JD,
       count the match (handles reordering like "developer ai").

    Returns the canonical role key and its skill dict, or (None, None).
    """
    jd_lower = jd.lower()
    jd_tokens = set(re.findall(r"[a-z][a-z0-9#.+/'-]*", jd_lower))

    best_canonical: str | None = None
    best_skill_dict: dict[str, list[str]] | None = None
    best_overlap: int = 0

    for canonical, skill_dict in ROLE_SKILL_MAP.items():
        # Exact substring
        if canonical in jd_lower:
            return canonical, skill_dict

        # Token overlap — require ≥ 2 meaningful role tokens to match
        role_tokens = set(re.findall(r"[a-z][a-z0-9#.+/'-]*", canonical))
        role_tokens -= _COUNT_STOPWORDS
        if len(role_tokens) < 2:
            continue
        overlap = len(role_tokens & jd_tokens)
        if overlap >= 2 and overlap > best_overlap:
            best_overlap = overlap
            best_canonical = canonical
            best_skill_dict = skill_dict

    return best_canonical, best_skill_dict  # type: ignore[return-value]


def _flatten_skills(skill_dict: dict[str, list[str]]) -> list[str]:
    """Combine core_skills + tools + concepts, deduplicate, cap at MAX_EXPANSION_SKILLS."""
    seen: set[str] = set()
    result: list[str] = []

    # Priority: core_skills first, then tools, then concepts
    for bucket in ("core_skills", "tools", "concepts"):
        for skill in skill_dict.get(bucket, []):
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                result.append(skill)
            if len(result) >= MAX_EXPANSION_SKILLS:
                return result

    return result
