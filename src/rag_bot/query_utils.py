
import re
import logging
logger = logging.getLogger(__name__)

def preprocess_query(query: str) -> str:
    """
    Preprocess user query before retrieval.

    Current steps:
    - strip whitespace
    - normalize spaces
    - remove accidental newlines

    Future extensions:
    - query rewriting
    - keyword expansion
    - spell correction
    """

    if not query:
        return ""

    # Remove extra whitespace
    logger.info(f"Original query: {query}")
    query = query.strip()

    # Normalize spaces
    processed_query = re.sub(r"\s+", " ", query)

    logger.info(f"Processed query: {processed_query}")

    return processed_query