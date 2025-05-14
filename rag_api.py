from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from text.cleaners import spanish_cleaner_with_accents
import os

app = FastAPI(title="Spanish RAG API")

class Query(BaseModel):
    text: str

class Response(BaseModel):
    answer: str
    sources: list[str]

def load_vault():
    """Load the processed documents from vault.txt"""
    if not os.path.exists("vault.txt"):
        return []
    
    with open("vault.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_relevant_chunks(query: str, chunks: list[str], top_k: int = 3):
    """Get the most relevant chunks for the query using Ollama embeddings"""
    # Get query embedding
    query_embedding = ollama.embeddings(model="mxbai-embed-large", prompt=query)["embedding"]
    
    # Get chunk embeddings
    chunk_embeddings = []
    for chunk in chunks:
        embedding = ollama.embeddings(model="mxbai-embed-large", prompt=chunk)["embedding"]
        chunk_embeddings.append(embedding)
    
    # Calculate cosine similarity
    similarities = []
    for chunk_emb in chunk_embeddings:
        similarity = sum(a * b for a, b in zip(query_embedding, chunk_emb))
        similarities.append(similarity)
    
    # Get top k chunks
    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_indices]

@app.post("/query", response_model=Response)
async def query_rag(query: Query):
    try:
        # Clean and normalize the query
        cleaned_query = spanish_cleaner_with_accents(query.text)
        
        # Load the vault
        chunks = load_vault()
        if not chunks:
            raise HTTPException(status_code=404, detail="No documents found in vault.txt")
        
        # Get relevant chunks
        relevant_chunks = get_relevant_chunks(cleaned_query, chunks)
        
        # Create context from relevant chunks
        context = "\n".join(relevant_chunks)
        
        # Generate response using Ollama
        prompt = f"""Contexto: {context}

Pregunta: {cleaned_query}

Por favor, responde la pregunta basándote en el contexto proporcionado. Si la respuesta no está en el contexto, di que no tienes suficiente información."""

        response = ollama.generate(model="llama2", prompt=prompt)
        
        return Response(
            answer=response["response"],
            sources=relevant_chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 