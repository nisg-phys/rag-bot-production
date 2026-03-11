import logging
import time

from annotated_types import doc
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
os.environ["TOKENIZERS_PARALLELISM"] = "true"

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda

from rag_bot.config import VECTOR_DB_DIR, RETRIEVAL_K
from rag_bot.query_utils import preprocess_query
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor, TimeoutError

load_dotenv()



class RAGPipeline:

  
    def __init__(self):
        self.cache = {}
        self.llm = self._get_llm()
        self.chain = self._build_chain()

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)

    def run_with_timeout(self, query: str, timeout: int = 20):

        with ThreadPoolExecutor() as executor:

            future = executor.submit(self.run_chain_with_retry, query)

            try:
                return future.result(timeout=timeout)

            except TimeoutError:
                logger.error("LLM call timed out")
                raise

    def run_chain_with_retry(self, query: str):
        return self.chain.invoke(query)

    def log_prompt(self,prompt_value):
        logger.info("Prompt sent to LLM:")
        logger.info(prompt_value.to_string())
        return prompt_value
    
    

    def _get_llm(self):
        provider = os.getenv("LLM_PROVIDER", "groq").lower()

        if provider == "openai":
            return ChatOpenAI(
                model="mistralai/devstral-2512:free",
                openai_api_base ="https://openrouter.ai/api/v1"
            )

        if provider == "huggingface":
            llm = HuggingFaceEndpoint(
            repo_id= "google/flan-t5-large",
            task="question-answering", # Adjust task as needed (e.g., "question-answering")
            max_new_tokens=128,
            temperature=0.1, # Set temperature to 0 for more deterministic, factual responses
)
            return ChatHuggingFace(llm=llm)

        return ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    def _build_chain(self):
        log_prompt_runnable = RunnableLambda(self.log_prompt)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vectorstore = Chroma(
            persist_directory= VECTOR_DB_DIR,
            embedding_function=embeddings,
        )

        self.vectorstore = vectorstore


        retriever = vectorstore.as_retriever(search_kwargs=RETRIEVAL_K)
        self.retriever = retriever

        prompt = ChatPromptTemplate.from_template(
            """
You are a helpful assistant well versed in government policies and schemes. 
Answer the question ONLY using the context below. If you do not know the answer refuse politely.

<context>
{context}
</context>

Question: {input}
"""
        )

        rag_chain = (
            {
                "context": retriever,
                "input": RunnablePassthrough(),
            }
            | prompt
            | log_prompt_runnable
            | self.llm
            | StrOutputParser()
        )

        return rag_chain

    def query(self, question: str) -> str:

        start_time = time.perf_counter()

        if question in self.cache:
            logger.info("Cache hit")
            return self.cache[question]
        
        logger.info("Cache miss")



        try:

            processed = preprocess_query(question)

            docs = self.retriever.invoke(processed)

            results = self.vectorstore.similarity_search_with_score(
            processed,
            k=RETRIEVAL_K['k']
       
)
        

            logger.info(f"Retrieved {len(docs)} documents")

            for i, (doc, score) in enumerate(results):
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page", "unknown")
                chunk_length = len(doc.page_content)
                logger.info(f"Source: {source}| page {page} | chunk_length: {chunk_length}| similarity_score: {score:.3f}")
            


            answer = self.run_with_timeout(processed)
            

            duration = time.perf_counter() - start_time
            logger.info(f"RAG pipeline completed in {duration:.3f} seconds")

            return answer

        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.exception(f"RAG pipeline failed after {duration:.3f} seconds")
            return "Sorry, something went wrong while processing your question."