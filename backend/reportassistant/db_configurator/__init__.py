from common.vectordb.embeddings import BgeM3EmbeddingsModel


def preload_model():
    BgeM3EmbeddingsModel().get_model().encode_documents(["hello"])
    return

preload_model()