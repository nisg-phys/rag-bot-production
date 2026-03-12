import logging
import time
from typing import Optional
from rag_bot.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Logging system initialized successfully")
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager

from rag_bot.pipeline import RAGPipeline
from fastapi import HTTPException
import asyncio

# Global variable to track pipeline
pipeline_instance: Optional[RAGPipeline] = None
is_initializing = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_instance, is_initializing
    
    # Start initialization in background - DON'T wait for it
    async def init_pipeline():
        global pipeline_instance, is_initializing
        is_initializing = True
        logger.info("Initializing RAG Pipeline in background...")
        try:
            # Run blocking initialization in thread pool
            pipeline_instance = await asyncio.to_thread(RAGPipeline)
            app.state.pipeline = pipeline_instance
            logger.info("RAG Pipeline ready!")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
        finally:
            is_initializing = False
    
    # Start initialization task but don't wait for it
    asyncio.create_task(init_pipeline())
    logger.info("Startup complete, pipeline loading in background...")
    
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

@app.get("/health")
def health():
    """Health check endpoint"""
    global pipeline_instance, is_initializing
    if pipeline_instance is not None:
        return {"status": "ready", "pipeline": "loaded"}
    elif is_initializing:
        return {"status": "initializing", "pipeline": "loading"}
    else:
        return {"status": "error", "pipeline": "failed"}

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest, req: Request):
    global pipeline_instance, is_initializing
    
    # Check if pipeline is ready
    if pipeline_instance is None:
        if is_initializing:
            raise HTTPException(
                status_code=503,
                detail="RAG Pipeline is still initializing. Please try again in a moment."
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="RAG Pipeline failed to initialize."
            )
    
    pipeline = pipeline_instance
    start_time = time.perf_counter()
    logger.info(f"Received query: {request.question}")
    
    try:
        answer = pipeline.query(request.question)
        duration = time.perf_counter() - start_time
        logger.info(f"Query processed successfully in {duration:.3f} seconds.")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing query."
        )