# Spanish RAG System

A Retrieval-Augmented Generation (RAG) system for Spanish language processing using Ollama models.

## Configuration

The system uses a YAML configuration file (`config.yaml`) to manage model settings and parameters:

```yaml
models:
  llm: mistral          # Main language model for text generation
  embedding: mxbai-embed-large  # Model for creating embeddings

parameters:
  temperature: 0.7      # Controls randomness in model output
  max_tokens: 2048      # Maximum tokens in model response
```

### Available Models

You can change the models in `config.yaml` to use different Ollama models. Some options include:

- LLM Models:
  - mistral
  - llama2
  - codellama
  - neural-chat
  - starling-lm

- Embedding Models:
  - mxbai-embed-large
  - nomic-embed-text
  - all-MiniLM-L6-v2

## Setup and Running

1. Ensure you have Python 3.8+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
4. Install Ollama from [ollama.ai](https://ollama.ai)
5. Run the system:
   ```bash
   llm-api.bat  # Windows
   ```

## System Components

The system consists of several components:

1. **Model Management**
   - Automatically checks and loads required models
   - Handles model verification and error checking
   - Supports dynamic model switching through configuration

2. **Knowledge Base Processing**
   - Processes and indexes the knowledge base
   - Creates embeddings for efficient retrieval

3. **API Service**
   - Provides REST API endpoints for RAG functionality
   - Handles model inference and response generation

## Environment Variables

The system uses a `.env` file for environment-specific configurations. Create a `.env` file with your settings:

```env
# Add your environment variables here
```

## Error Handling

The system includes comprehensive error handling for:
- Model loading failures
- Configuration issues
- API startup problems
- Knowledge base processing errors

## Customization

To customize the system:

1. Modify `config.yaml` to change models or parameters
2. Adjust environment variables in `.env`
3. Modify the knowledge base processing in `process_knowledge.py`
4. Customize API endpoints in `rag_api.py`

## Requirements

See `requirements.txt` for full dependency list. Key dependencies include:
- openai>=1.0.0
- torch>=2.0.0
- PyPDF2>=3.0.0
- ollama>=0.1.0
- pyyaml>=6.0.0
- fastapi>=0.100.0
- uvicorn[standard]>=0.23.0
