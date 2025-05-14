import os
import re
import json
import PyPDF2
from text.cleaners import spanish_cleaner, spanish_cleaner_with_accents

def process_text_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as txt_file:
        text = txt_file.read()
        return process_text(text)

def process_pdf_file(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text() + " "
        return process_text(text)

def process_json_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)
        text = json.dumps(data, ensure_ascii=False)
        return process_text(text)

def process_text(text):
    # First, clean and normalize the text using Spanish text processing
    # We'll use the version that preserves accents for better Spanish understanding
    cleaned_text = spanish_cleaner_with_accents(text)
    
    # Split text into chunks by sentences, respecting a maximum chunk size
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < 1000:
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def main():
    # Clear the vault.txt file
    with open("vault.txt", "w", encoding="utf-8") as vault_file:
        vault_file.write("")
    
    # Process all files in the knowledge directory
    knowledge_dir = "knowledge"
    for filename in os.listdir(knowledge_dir):
        file_path = os.path.join(knowledge_dir, filename)
        
        if filename.endswith('.txt'):
            chunks = process_text_file(file_path)
        elif filename.endswith('.pdf'):
            chunks = process_pdf_file(file_path)
        elif filename.endswith('.json'):
            chunks = process_json_file(file_path)
        else:
            print(f"Skipping unsupported file: {filename}")
            continue
        
        # Append chunks to vault.txt
        with open("vault.txt", "a", encoding="utf-8") as vault_file:
            for chunk in chunks:
                vault_file.write(chunk.strip() + "\n")
        
        print(f"Processed {filename}")

if __name__ == "__main__":
    main() 