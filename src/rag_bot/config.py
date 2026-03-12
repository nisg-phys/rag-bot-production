from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"  # adjust path to where your db actually is
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

RETRIEVAL_K = {"k":3}

DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_LLM = "groq"
