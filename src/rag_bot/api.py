import logging
import time
from rag_bot.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Logging system initialized successfully")
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager

from rag_bot.pipeline import RAGPipeline
from fastapi import HTTPException



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAG Pipeline...")
    app.state.pipeline = RAGPipeline()
    logger.info("RAG Pipeline ready.")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest, req: Request):
    pipeline = req.app.state.pipeline
    start_time = time.perf_counter()
    logger.info(f"Recieved query: {request.question}")
    try:
        answer = pipeline.query(request.question)
        duration = time.perf_counter()-start_time
        logger.info(f"Query processed successfully in {duration:.3f} seconds.")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing query."
        )
