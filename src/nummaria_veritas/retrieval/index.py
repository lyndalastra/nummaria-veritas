"""Build the lexical TF-IDF retrieval index."""

from dataclasses import dataclass

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from nummaria_veritas.models import IngestedChunk


@dataclass
class LexicalIndex:
    vectorizer: TfidfVectorizer
    matrix: csr_matrix
    chunks: list[IngestedChunk]


def build_lexical_index(
    chunks: list[IngestedChunk],
) -> LexicalIndex:
    if not chunks:
        raise ValueError("Cannot build an index from an empty corpus.")

    texts = [chunk.text for chunk in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True,
    )

    matrix = vectorizer.fit_transform(texts).tocsr()

    return LexicalIndex(
        vectorizer=vectorizer,
        matrix=matrix,
        chunks=chunks,
    )
