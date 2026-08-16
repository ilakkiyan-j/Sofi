import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import BACKEND_ROOT
from tools.logger import log

LANCE_DB_AVAILABLE = False
try:
    import lancedb
    LANCE_DB_AVAILABLE = True
except ImportError:
    LANCE_DB_AVAILABLE = False

# Fallback to ChromaDB if LanceDB not present yet
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorRAGEngine:
    """
    L3 Semantic Memory & Local Document RAG System.
    Stores personal memories and indexes local documents for vector retrieval.
    Uses LanceDB with fallback to ChromaDB.
    """
    def __init__(self, db_dir: Optional[Path] = None):
        self.db_dir = db_dir or (BACKEND_ROOT / "lance_data")
        self.db_dir.mkdir(exist_ok=True, parents=True)
        self.lance_db = None
        self.chroma_client = None
        self.chroma_collection = None

        self._init_database()

    def _init_database(self):
        if LANCE_DB_AVAILABLE:
            try:
                log(f"💾 Initializing LanceDB at {self.db_dir}")
                self.lance_db = lancedb.connect(str(self.db_dir))
                log("✅ LanceDB connected successfully!")
                return
            except Exception as e:
                log(f"⚠️ LanceDB connection error: {e}")

        if CHROMADB_AVAILABLE:
            try:
                os.environ["ANONYMIZED_TELEMETRY"] = "False"
                self.chroma_client = chromadb.Client()
                self.chroma_collection = self.chroma_client.get_or_create_collection("sofi_semantic_memory")
                log("✅ ChromaDB fallback initialized.")
            except Exception as e:
                log(f"⚠️ ChromaDB init error: {e}")

    def add_memory(self, fact_text: str, reply: str) -> bool:
        """Stores explicit personal memories."""
        if not fact_text.strip():
            return False

        doc_id = hashlib.md5(fact_text.encode('utf-8')).hexdigest()[:12]
        content = f"User shared: {fact_text}\nContext/Reply: {reply}"

        try:
            if self.chroma_collection:
                self.chroma_collection.add(
                    documents=[content],
                    ids=[doc_id]
                )
                log(f"💾 Personal fact stored in vector memory: {doc_id}")
                return True
        except Exception as e:
            log(f"Memory save error: {e}")
        return False

    def query_memories(self, query: str, top_k: int = 3) -> str:
        """Retrieves top-k relevant personal facts for a given query."""
        if not query.strip():
            return ""

        try:
            if self.chroma_collection:
                results = self.chroma_collection.query(query_texts=[query], n_results=top_k)
                docs = results.get("documents", [[]])[0]
                return "\n".join(docs)
        except Exception as e:
            log(f"Memory retrieval error: {e}")
        return ""

    def index_document_chunk(self, doc_name: str, chunk_text: str, chunk_idx: int) -> bool:
        """Indexes a document text chunk for local RAG retrieval."""
        chunk_id = f"{doc_name}_{chunk_idx}_{hashlib.md5(chunk_text.encode()).hexdigest()[:6]}"
        try:
            if self.chroma_collection:
                self.chroma_collection.add(
                    documents=[f"[Source: {doc_name}]\n{chunk_text}"],
                    ids=[chunk_id]
                )
                return True
        except Exception as e:
            log(f"Document index chunk error: {e}")
        return False


# Global singleton vector RAG engine
rag_engine = VectorRAGEngine()
