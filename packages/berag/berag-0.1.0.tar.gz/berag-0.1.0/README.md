# 🧠 BeRAG

BeRAG is a modular Python library for Retrieval-Augmented Generation (RAG) systems built from your own data.

## Features
- Load and chunk documents
- Generate embeddings
- Store and retrieve using vector DBs
- Ask questions via LLMs

## Installation
```bash
pip install berag
```

## Usage
```python
from berag import RAGPipeline
rag = RAGPipeline(config="config.yaml")
rag.ask("What is BeRAG?")
```
