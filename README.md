# Ollama RAG (Retrieval-Augmented Generation) System

A powerful RAG system built with Ollama, FastAPI, and Python that enables intelligent document querying and response generation with customizable personalities. The system is designed to work with any Ollama-compatible model, giving you the flexibility to choose the best model for your needs.

## Features

- 🤖 Compatible with any Ollama model (Mistral, Llama2, Mixtral, etc.)
- 📚 Document processing and embedding generation
- 🔍 Semantic search capabilities
- 🎭 Customizable AI personalities
- 🌐 RESTful API interface
- 📝 Support for multiple document formats
- 🔒 Local processing for enhanced privacy

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Windows OS (for batch files) or Linux/Mac (with script modifications)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/josepheudave/ollama-RAG.git
cd ollama-RAG
```

## Run the setup script:
```bash
# On Windows
setup.bat
# On Linux/Mac
python setup.py
```

## Configuration

The system is configured through `config.yaml`. Key settings include:

- `ollama_model`: The Ollama model to use (e.g., "mistral", "llama2", "mixtral", etc.)
- `top_k`: Number of relevant chunks to retrieve
- `personality`: AI personality configuration
- `model`: Embedding model settings

You can use any model available in Ollama by changing the `ollama_model` setting in the configuration file.

## Knowledge Base Setup

1. Create a `knowledge` directory in the project root:
```bash
mkdir knowledge
```

2. Place your text files in the `knowledge` directory. Supported formats:
   - Text files (.txt)
   - PDF files (.pdf)
   - Other text-based documents

3. The system will process these files and create embeddings for semantic search.

## API Usage

1. Start the API server:
```bash
# On Windows
llm-api.bat
# On Linux/Mac
python rag_api.py
```

2. The API will be available at `http://localhost:8000`

3. Example API call:
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"text": "Your question here"}
)
print(response.json())
```

## API Endpoints

### POST /query
Query the RAG system with a question.

Request body:
```json
{
    "text": "Your question here"
}
```

Response:
```json
{
    "answer": "AI response",
    "sources": ["Relevant source 1", "Relevant source 2"]
}
```

## Project Structure

- `rag_api.py`: Main FastAPI application
- `process_knowledge.py`: Document processing utilities
- `config.yaml`: Configuration settings
- `knowledge/`: Directory for your knowledge base files
- `text/`: Text processing utilities
- `requirements.txt`: Python dependencies

## License

This project is licensed under MIT License
