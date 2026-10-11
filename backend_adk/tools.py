from __future__ import annotations

from backend_adk.text_analysis import extract_keywords


def match_job_skills(job_description: str, candidate_experience: str) -> dict[str, object]:
    """Compare explicit role keywords with the candidate's own experience text.

    Use this for a rough keyword overlap, not to assess qualifications or invent experience.
    Returns the overlap percentage and lists of matched and unmentioned terms.
    """
    required = extract_keywords(job_description)
    evidence = extract_keywords(candidate_experience)
    matched = sorted(required & evidence)
    missing = sorted(required - evidence)
    return {
        "overlap_percent": round(100 * len(matched) / max(len(required), 1)),
        "matched_terms": matched[:12],
        "unmentioned_terms": missing[:12],
        "qualification_score": False,
    }

def search_interview_research(company: str, role: str) -> dict[str, object]:
    """Return an offline research checklist when live Google Search is unavailable."""
    return {
        "status": "mock",
        "notice": "Illustrative research prompts only. No live search was performed.",
        "markdown": (
            f"- Read {company}'s engineering blog for architecture and reliability decisions.\n"
            f"- Compare the {role} responsibilities with current product challenges.\n"
            "- Prepare a question grounded in a source you verify before the interview."
        ),
        "sources": [],
    }

def get_interview_question_trends(role: str) -> dict[str, object]:
    """Return clearly labeled sample question counts for an offline session."""
    rows = [
        {"question_type": "System design", "sample_count": 42},
        {"question_type": "Data structures", "sample_count": 36},
        {"question_type": "Behavioral", "sample_count": 29},
    ]
    markdown = "| Question category | Sample count |\n| --- | ---: |\n" + "\n".join(
        f"| {row['question_type']} | {row['sample_count']} |" for row in rows
    )
    return {
        "status": "mock",
        "notice": f"Illustrative local rows for {role}; no cloud query ran.",
        "markdown": markdown,
        "rows": rows,
    }