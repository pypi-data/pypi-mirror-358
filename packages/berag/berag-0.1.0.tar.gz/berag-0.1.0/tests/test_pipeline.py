from berag import RAGPipeline

def test_ask():
    pipeline = RAGPipeline()
    assert "Simulated answer" in pipeline.ask("What is RAG?")
