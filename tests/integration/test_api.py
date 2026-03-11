from fastapi.testclient import TestClient
from rag_bot.api import app

client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}



class FakePipeline:
    def query(self, question: str):
        return "mock answer"


client = TestClient(app)

# override the pipeline
app.state.pipeline = FakePipeline()


def test_query_endpoint():

    payload = {
        "question": "How many projects were sanctioned?"
    }

    response = client.post("/query", json=payload)

    assert response.status_code == 200
    assert response.json()["answer"] == "mock answer"
