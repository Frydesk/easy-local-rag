from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import ollama
from text.cleaners import spanish_cleaner_with_accents
import os
import yaml
import json
import codecs
import asyncio

app = FastAPI(title="Spanish RAG API")

# Load configuration with UTF-8 BOM
with codecs.open("config.yaml", "r", encoding="utf-8-sig") as f:
    config = yaml.safe_load(f)

class Query(BaseModel):
    text: str

class Response(BaseModel):
    answer: str
    sources: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "This is a sample response",
                "sources": ["Source 1", "Source 2"]
            }
        }

def load_vault():
    """Load the processed documents from vault.txt"""
    if not os.path.exists("vault.txt"):
        return []
    
    with codecs.open("vault.txt", "r", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]

def get_relevant_chunks(query: str, chunks: list[str], top_k: int = None):
    """Get the most relevant chunks for the query using Ollama embeddings"""
    if top_k is None:
        top_k = config["model"]["top_k_chunks"]
        
    # Get query embedding
    query_embedding = ollama.embeddings(model=config["model"]["embedding_model"], prompt=query)["embedding"]
    
    # Get chunk embeddings
    chunk_embeddings = []
    for chunk in chunks:
        embedding = ollama.embeddings(model=config["model"]["embedding_model"], prompt=chunk)["embedding"]
        chunk_embeddings.append(embedding)
    
    # Calculate cosine similarity
    similarities = []
    for chunk_emb in chunk_embeddings:
        similarity = sum(a * b for a, b in zip(query_embedding, chunk_emb))
        similarities.append(similarity)
    
    # Get top k chunks
    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_indices]

async def process_query(query_text: str):
    try:
        # Clean and normalize the query
        cleaned_query = spanish_cleaner_with_accents(query_text)
        
        # Load the vault
        chunks = load_vault()
        if not chunks:
            raise Exception("No documents found in vault.txt")
        
        # Get relevant chunks
        relevant_chunks = get_relevant_chunks(cleaned_query, chunks)
        
        # Create context from relevant chunks
        context = "\n".join(relevant_chunks)
        
        # Generate response using Ollama with personality from config
        personality = config["personality"]
        prompt = config["prompt_template"].format(
            context=context,
            query=cleaned_query,
            personality={
                "name": personality["name"],
                "description": personality["description"],
                "traits": personality["traits"],
                "response_constraints": personality["response_constraints"]
            }
        )

        messages = [
            {"role": "system", "content": config["system_message"]},
            {"role": "user", "content": prompt}
        ]

        response = ollama.chat(
            model=config["ollama_model"],
            messages=messages,
            options=config["model"]["parameters"]
        )
        
        if not response:
            raise Exception("Empty response from Ollama")
            
        # Handle both dictionary and object responses
        if isinstance(response, dict):
            if 'message' not in response or 'content' not in response['message']:
                raise Exception("Invalid response format from Ollama")
            answer = response['message']['content']
        else:
            if not hasattr(response, 'message') or not hasattr(response.message, 'content'):
                raise Exception("Invalid response format from Ollama")
            answer = response.message.content
        
        # Ensure proper UTF-8 BOM encoding
        answer = answer.encode('utf-8-sig', errors='ignore').decode('utf-8-sig')
        
        return {
            "answer": answer,
            "sources": relevant_chunks
        }
    
    except Exception as e:
        raise Exception(f"Error in process_query: {str(e)}")

@app.websocket("/airesponse")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # Wait for any message (text or JSON)
                message = await websocket.receive_text()
                
                # Try to parse as JSON
                try:
                    message_data = json.loads(message)
                    if not isinstance(message_data, dict) or 'type' not in message_data or 'content' not in message_data:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid message format. Expected {type: string, content: string}"
                        })
                        continue
                    query_text = message_data['content']
                except json.JSONDecodeError:
                    # If not JSON, treat the message as plain text query
                    query_text = message
                
                print(f"\nUser: {query_text}")  # Print user's query
                
                # Process the query
                try:
                    result = await process_query(query_text)
                    # Print just the answer to console
                    print(f"Dr. Simi: {result['answer']}\n")
                    await websocket.send_json({
                        "type": "answer",
                        "data": result
                    })
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error: {error_msg}")
                    await websocket.send_json({
                        "type": "error",
                        "message": error_msg
                    })

            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except Exception as e:
                print(f"Error in message processing: {str(e)}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                except:
                    pass

    except Exception as e:
        print(f"Error in websocket connection: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100) 