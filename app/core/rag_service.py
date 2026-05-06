import os
import json
import shutil
from pathlib import Path

# Environment settings for cleaner terminal output
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

class RAGService:
    """
    Simplified Retrieval-Augmented Generation service.
    Handles document indexing and similarity search with terminal logging.
    """

    def __init__(self, config):
        self.config = config
        self.base_dir = Path(__file__).resolve().parent.parent
        self.mode = self.config.get("mode", "online")
        
        # Paths
        self.db_path = self.base_dir / "data" / "vector_db" / self.mode
        self.kb_path = self.base_dir / "data" / "knowledge_base"
        self.index_tracker_path = self.base_dir / "data" / f"indexed_files_{self.mode}.json"

        # Ensure directories exist
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.kb_path.mkdir(parents=True, exist_ok=True)

        self._embeddings = None
        self.vector_db = None

        print(f"\n[RAG System] Initializing in {self.mode.upper()} mode...")
        self._startup()

    def _startup(self):
        try:
            self.vector_db = self._load_db()
            self._index_knowledge_base()
            print("[RAG System] Ready and active. [OK]")
        except Exception as e:
            print(f"[RAG System] Startup Error: {e}")

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = self._init_embeddings()
        return self._embeddings

    def _init_embeddings(self):
        print(f"[RAG System] Loading embedding model for {self.mode} mode...")
        if self.mode == "local":
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            api_key = self.config.get("api_key", "")
            if not api_key:
                print("[!] [RAG System] No API key found. Falling back to Local embeddings.")
                from langchain_huggingface import HuggingFaceEmbeddings
                self.mode = "local"
                return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)

    def _load_db(self):
        from langchain_community.vectorstores import FAISS
        index_file = self.db_path / "index.faiss"
        
        if not index_file.exists():
            print(f"[RAG System] No existing database found at {self.db_path}. Will create new one.")
            return None

        try:
            db = FAISS.load_local(str(self.db_path), self.embeddings, allow_dangerous_deserialization=True)
            print(f"[RAG System] Loaded existing vector database ({self.mode}).")
            return db
        except Exception as e:
            print(f"[!] [RAG System] Failed to load DB: {e}. Starting fresh.")
            self._reset_db()
            return None

    def _reset_db(self):
        if self.db_path.exists():
            shutil.rmtree(str(self.db_path), ignore_errors=True)
        self.db_path.mkdir(parents=True, exist_ok=True)
        if self.index_tracker_path.exists():
            self.index_tracker_path.unlink()
        print("[RAG System] Database reset.")

    def _index_knowledge_base(self):
        """Scan knowledge_base folder for new files."""
        indexed = self._get_tracker()
        updated = False

        for file_path in self.kb_path.iterdir():
            if file_path.suffix.lower() not in {".txt", ".pdf"}:
                continue
            
            mtime = str(file_path.stat().st_mtime)
            if indexed.get(str(file_path)) == mtime:
                continue

            print(f"[RAG System] Auto-indexing KB file: {file_path.name}")
            if self.add_document(str(file_path)):
                indexed[str(file_path)] = mtime
                updated = True

        # Clean up tracker for files that no longer exist
        for path in list(indexed.keys()):
            if not os.path.exists(path):
                print(f"[RAG System] Removing missing file from index tracker: {os.path.basename(path)}")
                del indexed[path]
                updated = True

        if updated:
            self._save_tracker(indexed)

    def _get_tracker(self):
        if self.index_tracker_path.exists():
            with open(self.index_tracker_path, "r") as f:
                return json.load(f)
        return {}

    def _save_tracker(self, data):
        with open(self.index_tracker_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_document(self, file_path: str, task_context: str = "") -> bool:
        """Chunk and add a document. task_context is prepended to chunks for better RAG."""
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        
        if not os.path.exists(file_path):
            print(f"[!] [RAG System] File not found: {file_path}")
            return False

        try:
            docs = self._load_file(file_path)
            if not docs: return False

            splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
            chunks = splitter.split_documents(docs)
            
            # Context Injection: Add task name to each chunk so the AI knows WHY this file is here
            if task_context:
                print(f"[RAG System] Injecting task context: '{task_context}' into {len(chunks)} chunks.")
                for c in chunks:
                    c.page_content = f"CONTEXT (Task: {task_context}):\n{c.page_content}"

            # Metadata for logging
            for c in chunks: c.metadata["source"] = os.path.basename(file_path)

            if self.vector_db is None:
                self.vector_db = FAISS.from_documents(chunks, self.embeddings)
            else:
                self.vector_db.add_documents(chunks)

            self.vector_db.save_local(str(self.db_path))
            print(f"[RAG System] Indexed {len(chunks)} chunks from: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            print(f"[!] [RAG System] Error indexing {file_path}: {e}")
            return False

    def index_task(self, task_name: str, category: str = ""):
        """Index a task description directly as a searchable document."""
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS
        
        content = f"Task: {task_name}"
        if category: content += f" (Category: {category})"
        
        doc = Document(page_content=content, metadata={"source": "Task List"})
        
        if self.vector_db is None:
            self.vector_db = FAISS.from_documents([doc], self.embeddings)
        else:
            self.vector_db.add_documents([doc])
        
        self.vector_db.save_local(str(self.db_path))
        print(f"[RAG System] Indexed task: {task_name}")

    def _load_file(self, file_path: str):
        from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
        try:
            if file_path.lower().endswith(".pdf"):
                return PyMuPDFLoader(file_path).load()
            return TextLoader(file_path, encoding="utf-8").load()
        except Exception as e:
            print(f"[!] [RAG System] Load Error ({os.path.basename(file_path)}): {e}")
            return []

    def query(self, query_text: str, k: int = 4, threshold: float = 0.4) -> str:
        """Search the database and return context string."""
        if self.vector_db is None:
            return ""

        print(f"\n[RAG System] Querying: \"{query_text}\"")
        try:
            results = self.vector_db.similarity_search_with_score(query_text, k=k)
            
            final_chunks = []
            sources = set()
            
            for doc, score in results:
                # FAISS score is L2 distance (lower is better)
                # Simple normalization for logging: 1 / (1 + score)
                similarity = 1.0 / (1.0 + score)
                
                if similarity >= threshold:
                    final_chunks.append(doc.page_content)
                    sources.add(doc.metadata.get("source", "unknown"))
                    print(f"   [MATCH] Found in [{doc.metadata.get('source')}] (Score: {similarity:.2f})")
                else:
                    print(f"   [SKIP] Weak match (Score: {similarity:.2f})")

            if final_chunks:
                print(f"[RAG System] Found {len(final_chunks)} relevant chunks from {len(sources)} sources.")
                return "\n\n".join(final_chunks)
            
            print("[RAG System] No relevant information found in database.")
            return ""

        except Exception as e:
            print(f"[!] [RAG System] Query Error: {e}")
            return ""

    @property
    def knowledge_base_path(self):
        return self.kb_path

    def refresh_knowledge_base(self):
        self._index_knowledge_base()
