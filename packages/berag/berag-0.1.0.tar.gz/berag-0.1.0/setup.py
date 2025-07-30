from setuptools import setup, find_packages

setup(
    name="berag",
    version="0.1.0",
    author="Besanty Ezekiel",
    description="A modular RAG pipeline library for your own data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_github_username/berag",
    packages=find_packages(),
    install_requires=[
        "openai",
        "chromadb",
        "sentence-transformers",
        "langchain",
        "tqdm",
        "PyYAML",
        "pypdf"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
