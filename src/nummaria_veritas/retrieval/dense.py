from dataclasses import dataclass
from datetime import date

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer

from nummaria_veritas.models import EvidenceResult, IngestedChunk


@dataclass
class DenseIndex:
    vectorizer: TfidfVectorizer
    svd: TruncatedSVD
    normalizer: Normalizer
    embeddings: np.ndarray
    chunks: list[IngestedChunk]


def build_dense_index(
    chunks: list[IngestedChunk],
    *,
    n_components: int = 256,
) -> DenseIndex:
    if not chunks:
        raise ValueError("Cannot build a dense index from an empty corpus.")

    texts = [chunk.text for chunk in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True,
    )

    tfidf_matrix = vectorizer.fit_transform(texts)

    max_components = min(
        n_components,
        tfidf_matrix.shape[0] - 1,
        tfidf_matrix.shape[1] - 1,
    )

    if max_components <= 0:
        raise ValueError("Corpus is too small to build a dense index.")

    svd = TruncatedSVD(
        n_components=max_components,
        random_state=42,
    )

    dense_matrix = svd.fit_transform(tfidf_matrix)

    normalizer = Normalizer(copy=False)
    embeddings = normalizer.fit_transform(dense_matrix)

    return DenseIndex(
        vectorizer=vectorizer,
        svd=svd,
        normalizer=normalizer,
        embeddings=embeddings,
        chunks=chunks,
    )


def retrieve_dense(
    index: DenseIndex,
    *,
    query: str,
    company: str,
    as_of_date: date,
    top_k: int = 5,
) -> list[EvidenceResult]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    eligible_indices = [
        index_position
        for index_position, chunk in enumerate(index.chunks)
        if chunk.company == company and chunk.publication_date <= as_of_date
    ]

    if not eligible_indices:
        return []

    query_tfidf = index.vectorizer.transform([query])
    query_dense = index.svd.transform(query_tfidf)
    query_embedding = index.normalizer.transform(query_dense)[0]

    eligible_embeddings = index.embeddings[eligible_indices]

    scores = eligible_embeddings @ query_embedding

    ranked_positions = np.argsort(scores)[::-1][:top_k]

    results: list[EvidenceResult] = []

    for position in ranked_positions:
        corpus_index = eligible_indices[int(position)]
        chunk = index.chunks[corpus_index]

        results.append(
            EvidenceResult(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                company=chunk.company,
                document_type=chunk.document_type,
                reporting_period=chunk.reporting_period,
                publication_date=chunk.publication_date,
                page_number=chunk.page_number,
                text=chunk.text,
                retrieval_score=float(scores[position]),
            )
        )

    return results
