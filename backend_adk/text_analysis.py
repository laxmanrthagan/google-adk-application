import re


STOPWORDS = {
    "a", "about", "after", "all", "also", "an", "and", "any", "are", "as", "at",
    "be", "been", "being", "but", "by", "can", "could", "do", "does", "for", "from",
    "had", "has", "have", "how", "if", "in", "into", "is", "it", "its", "may", "more",
    "most", "must", "of", "on", "or", "our", "out", "over", "should", "some", "such",
    "than", "that", "the", "their", "them", "then", "there", "these", "they", "this",
    "those", "through", "to", "under", "up", "use", "used", "using", "was", "we", "were",
    "what", "when", "where", "which", "while", "who", "will", "with", "would", "you",
    "your", "experience", "looking", "role", "team", "teams", "work", "working",
}


def extract_keywords(value: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", value)
    return {
        word.lower().strip(".,;:!?()[]{}")
        for word in words
        if word.lower().strip(".,;:!?()[]{}") not in STOPWORDS
    }