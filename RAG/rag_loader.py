# rag_loader.py
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

def load_vectorstore(
    txt_path: str = "RAG\\incidents.txt",
    separator: str = "\n\n---\n\n",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model: str = "nomic-embed-text",
):
    """
    Load RAG documents from a plain-text file, split into chunks, embed with Ollama,
    and store in a FAISS vectorstore.
    """
    # 1. Load raw text documents (returns List[Document])
    loader = TextLoader(file_path=txt_path, encoding="utf-8")
    raw_docs = loader.load()  # <-- This is a list of Document

    # 2. Combine into one string (or process individually)
    full_text = "\n".join(doc.page_content for doc in raw_docs)

    # 3. Split into individual examples
    examples = full_text.split(separator)

    # 4. Convert each example into a Document
    docs = [Document(page_content=ex.strip()) for ex in examples if ex.strip()]

    # 5. Chunk long examples
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_docs = splitter.split_documents(docs)

    # 6. Embed with Ollama
    embeddings = OllamaEmbeddings(model=embedding_model)

    # 7. Build and return FAISS vector store
    vectorstore = FAISS.from_documents(chunked_docs, embeddings)
    return vectorstore
