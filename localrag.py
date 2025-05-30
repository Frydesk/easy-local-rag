import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
import yaml
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import time
import threading
from pathlib import Path

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Load configuration
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Function to get relevant context from the vault based on user input
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    # Compute cosine similarity between the input and vault embeddings
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Adjust top_k if it's greater than the number of available scores
    top_k = min(top_k, len(cos_scores))
    # Sort the scores and get the top-k indices
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Get the corresponding context from the vault
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

def rewrite_query(user_input_json, conversation_history, ollama_model, config):
    user_input = json.loads(user_input_json)["Query"]
    # Get the last 5 messages instead of 2
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
    
    # Use the prompt template from config
    prompt = config['query_rewrite_prompt'].format(
        context=context,
        user_input=user_input
    )
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})

class MemoryManager:
    def __init__(self, max_memory_size: int = 10, timeout_seconds: int = 60):
        self.max_memory_size = max_memory_size
        self.timeout_seconds = timeout_seconds
        self.memory_file = Path("memory.json")
        self.last_activity = time.time()
        self.goodbye_phrases = [
            'adios', 'hasta pronto', 'nos vemos', 'cuidate',
            'buen dia', 'buena tarde', 'buena noche', 'bye',
            'goodbye', 'see you', 'take care'
        ]
        
        # Initialize memory file if it doesn't exist
        if not self.memory_file.exists():
            self._save_memory({
                "conversations": [],
                "last_updated": time.time()
            })
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def _save_memory(self, memory_data):
        """Save memory data to file."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def _load_memory(self):
        """Load memory data from file."""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"conversations": [], "last_updated": time.time()}
    
    def _cleanup_loop(self):
        """Background thread to check for timeout and cleanup memory."""
        while True:
            time.sleep(10)  # Check every 10 seconds
            current_time = time.time()
            memory_data = self._load_memory()
            
            # Check for timeout
            if current_time - memory_data["last_updated"] > self.timeout_seconds:
                self._save_memory({
                    "conversations": [],
                    "last_updated": current_time
                })
    
    def add_interaction(self, role: str, content: str):
        """Add a new interaction to the conversation history."""
        memory_data = self._load_memory()
        current_time = time.time()
        
        # Check for goodbye message
        if role == "user" and any(phrase in content.lower() for phrase in self.goodbye_phrases):
            self._save_memory({
                "conversations": [],
                "last_updated": current_time
            })
            return
        
        # Add new interaction
        memory_data["conversations"].append({
            "role": role,
            "content": content,
            "timestamp": current_time
        })
        
        # Maintain max size
        if len(memory_data["conversations"]) > self.max_memory_size:
            memory_data["conversations"] = memory_data["conversations"][-self.max_memory_size:]
        
        memory_data["last_updated"] = current_time
        self._save_memory(memory_data)
        self.last_activity = current_time
    
    def get_relevant_context(self, current_query: str, ollama_model: str) -> str:
        """Get relevant context from memory based on the current query."""
        memory_data = self._load_memory()
        if not memory_data["conversations"]:
            return ""
        
        # Get all conversations
        all_context = []
        for conv in memory_data["conversations"]:
            all_context.append(f"{conv['role']}: {conv['content']}")
        
        # If we have too much context, use embeddings to find most relevant parts
        if len(all_context) > 5:
            # Get embedding for current query
            query_embedding = ollama.embeddings(model=ollama_model, prompt=current_query)["embedding"]
            
            # Get embeddings for all context
            context_embeddings = []
            for ctx in all_context:
                embedding = ollama.embeddings(model=ollama_model, prompt=ctx)["embedding"]
                context_embeddings.append(embedding)
            
            # Calculate similarities
            similarities = []
            for ctx_emb in context_embeddings:
                similarity = np.dot(query_embedding, ctx_emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(ctx_emb)
                )
                similarities.append(similarity)
            
            # Get top 5 most relevant contexts
            top_indices = np.argsort(similarities)[-5:]
            relevant_context = [all_context[i] for i in top_indices]
        else:
            relevant_context = all_context
        
        return "\n".join(relevant_context)
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        memory_data = self._load_memory()
        return memory_data["conversations"]

# Update the ollama_chat function to use MemoryManager
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, memory_manager: MemoryManager, config):
    # Add user input to memory
    memory_manager.add_interaction("user", user_input)
    
    # Get relevant context from memory
    memory_context = memory_manager.get_relevant_context(user_input, ollama_model)
    
    # Always use query rewriting for better context understanding
    query_json = {
        "Query": user_input,
        "Rewritten Query": ""
    }
    rewritten_query_json = rewrite_query(json.dumps(query_json), memory_manager.get_full_history(), ollama_model, config)
    rewritten_query_data = json.loads(rewritten_query_json)
    rewritten_query = rewritten_query_data["Rewritten Query"]
    print(PINK + "Original Query: " + user_input + RESET_COLOR)
    print(PINK + "Rewritten Query: " + rewritten_query + RESET_COLOR)
    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    # Combine memory context with document context
    user_input_with_context = user_input
    if memory_context:
        user_input_with_context += "\n\nConversation Context:\n" + memory_context
    if relevant_context:
        user_input_with_context += "\n\nDocument Context:\n" + context_str
    
    # Create messages array with system message and conversation history
    messages = [
        {"role": "system", "content": system_message},
        *memory_manager.get_full_history()
    ]
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    
    # Add assistant's response to memory
    memory_manager.add_interaction("assistant", response.choices[0].message.content)
    
    return response.choices[0].message.content

# Parse command-line arguments
print(NEON_GREEN + "Parsing command-line arguments..." + RESET_COLOR)
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
args = parser.parse_args()

# Load configuration
print(NEON_GREEN + "Loading configuration..." + RESET_COLOR)
config = load_config()

# Configuration for the Ollama API client
print(NEON_GREEN + "Initializing Ollama API client..." + RESET_COLOR)
client = OpenAI(
    base_url=config['ollama_api']['base_url'],
    api_key=config['ollama_api']['api_key']
)

# Load the vault content
print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
vault_content = []
if os.path.exists(config['vault_file']):
    with open(config['vault_file'], "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

# Generate embeddings for the vault content using Ollama
print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model=config['model']['embedding_model'], prompt=content)
    vault_embeddings.append(response["embedding"])

# Convert to tensor and print embeddings
print("Converting embeddings to tensor...")
vault_embeddings_tensor = torch.tensor(vault_embeddings) 
print("Embeddings for each line in the vault:")
print(vault_embeddings_tensor)

# Update the conversation loop to use memory_manager instead of conversation_history
print("Starting conversation loop...")
system_message = config['system_message']
memory_manager = MemoryManager(max_memory_size=10, timeout_seconds=60)

while True:
    try:
        user_input = input(NEON_GREEN + "\nYou: " + RESET_COLOR)
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print(NEON_GREEN + "Goodbye!" + RESET_COLOR)
            break
        
        response = ollama_chat(
            user_input,
            system_message,
            vault_embeddings_tensor,
            vault_content,
            args.model,
            memory_manager,
            config
        )
        print(NEON_GREEN + "\nAssistant: " + RESET_COLOR + response)
        
    except KeyboardInterrupt:
        print(NEON_GREEN + "\nGoodbye!" + RESET_COLOR)
        break
    except Exception as e:
        print(RED + f"Error: {str(e)}" + RESET_COLOR)
