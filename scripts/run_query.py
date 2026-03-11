import sys
import os

# Important for src layout
sys.path.append("src")

from rag_bot.pipeline import RAGPipeline


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_query.py 'your question here'")
        return

    question = sys.argv[1]

    pipeline = RAGPipeline()
    answer = pipeline.query(question)

    print("\n--- ANSWER ---\n")
    print(answer)


if __name__ == "__main__":
    main()