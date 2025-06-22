
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_chroma import Chroma

def load_vector_store(name: str) -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    return Chroma(
        collection_name="warframe",
        embedding_function=embeddings,
        persist_directory=f"./data/{name}",
    )