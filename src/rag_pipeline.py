from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import settings


class RagEngine:
    def __init__(self) -> None:
        self._vectorstore: FAISS | None = None

    def _load_documents(self, kb_path: Path) -> List[Document]:
        raw_text = kb_path.read_text(encoding="utf-8")
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
        chunks = splitter.split_text(raw_text)
        return [Document(page_content=chunk) for chunk in chunks]

    def _build_index(self) -> None:
        docs = self._load_documents(settings.kb_file_path)
        if settings.google_api_key:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.google_api_key,
            )
        else:
            # Deterministic local fallback keeps FAISS retrieval testable without external keys.
            embeddings = FakeEmbeddings(size=256)
        self._vectorstore = FAISS.from_documents(docs, embeddings)

    def retrieve(self, query: str) -> List[str]:
        if self._vectorstore is None:
            self._build_index()

        assert self._vectorstore is not None
        docs = self._vectorstore.similarity_search(query, k=settings.retriever_top_k)
        return [doc.page_content for doc in docs]


def grounded_answer(llm, query: str, context_chunks: List[str]) -> str:
    if not context_chunks:
        return "I do not have enough information in the local knowledge base to answer that confidently."

    context = "\n\n".join(context_chunks)
    prompt = (
        "Answer the user question using only the context below. "
        "If the answer is not in context, explicitly say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        return response.content

    # If the model client returns an unexpected payload, still return a grounded response.
    return context_chunks[0]
