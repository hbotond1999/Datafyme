from dataclasses import dataclass
from typing import Any

@dataclass
class EmbeddingsResult:
    """
    A data class to hold the result of the embedding process, which includes both sparse and dense vectors.

    Attributes:
        sparse_vectors (Any): The sparse representation of the input documents.
        dense_vectors (Any): The dense representation of the input documents.
    """
    sparse_vectors: Any
    dense_vectors: Any
