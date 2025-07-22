import torch
from milvus_model.hybrid.bge_m3 import BGEM3EmbeddingFunction

from common.vectordb.embeddings.schema import EmbeddingsResult


from typing import List

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Embedding model run in", device)
model = BGEM3EmbeddingFunction(model_name="BAAI/bge-m3", device=device)


class BgeM3EmbeddingsModel:
    """
    A class to interact with the BGE M3 embedding model, providing methods to generate
    sparse and dense vectors from input content and retrieve the dimensionality of dense vectors.
    """

    @classmethod
    def get_model(cls):
        """
        Get the BGE M3 embedding model instance. This model is cached for repeated use.

        Returns:
            BGEM3EmbeddingFunction: The embedding model initialized with the "BAAI/bge-m3" configuration.
        """
        return model

    @classmethod
    def create_sparse_dense_vectors(cls, contents: List[str]) -> EmbeddingsResult:
        """
        Generates sparse and dense embedding vectors from the given list of documents or text.

        Args:
            contents (List[str]): A list of text documents to encode into sparse and dense vectors.

        Returns:
            EmbeddingsResult: An object containing the resulting sparse and dense vectors.
        """
        result = cls.get_model().encode_documents(contents)
        return EmbeddingsResult(sparse_vectors=result["sparse"], dense_vectors=result["dense"])

    @classmethod
    def get_dense_dim(cls) -> int:
        """
        Get the dimensionality of the dense vectors produced by the BGE M3 model.

        Returns:
            int: The dimensionality of the dense vectors.
        """
        return cls.get_model().dim["dense"]
