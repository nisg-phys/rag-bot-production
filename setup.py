from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="rag-bot",
    version="0.1.0",
    author="Nishant Gupta",  # Change this to your name
    author_email="nishantgupta.phy@gmail.com",  # Change this
    description="RAG-based chatbot for querying government policy documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nisg-phys/RAG-BOT-MEMORY",
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Requirements
    python_requires=">=3.10",
    install_requires=[
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "langchain>=0.1.0",
    "langchain-community>=0.0.20",
    "langchain-groq>=0.0.1",        # Add this
    "langchain-openai>=0.0.5",      # Add this
    "langchain-huggingface>=0.0.1", # Add this
    "langchain-chroma>=0.1.0",      # Add this
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "streamlit>=1.29.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "PyYAML>=6.0",
    "structlog>=23.1.0",
    "tenacity>=8.2.0",
],
    
    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)