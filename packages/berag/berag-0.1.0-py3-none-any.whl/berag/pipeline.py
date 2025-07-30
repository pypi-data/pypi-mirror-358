class RAGPipeline:
    def __init__(self, config=None):
        self.config = config

    def ask(self, question):
        return f"Simulated answer to: {question}"
