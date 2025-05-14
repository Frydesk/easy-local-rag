import re

def clean_spanish_text(text):
    """
    Clean and normalize Spanish text.
    - Removes extra whitespace
    - Normalizes punctuation
    - Handles common Spanish abbreviations
    """
    # Convert to lowercase
    text = text.lower()
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize punctuation
    text = re.sub(r'\.{2,}', '.', text)  # Multiple dots to single dot
    text = re.sub(r'!{2,}', '!', text)   # Multiple exclamation marks to single
    text = re.sub(r'\?{2,}', '?', text)  # Multiple question marks to single
    
    # Handle common Spanish abbreviations
    text = re.sub(r'\bSr\.', 'señor', text)
    text = re.sub(r'\bSra\.', 'señora', text)
    text = re.sub(r'\bDr\.', 'doctor', text)
    text = re.sub(r'\bDra\.', 'doctora', text)
    text = re.sub(r'\bProf\.', 'profesor', text)
    text = re.sub(r'\bProfa\.', 'profesora', text)
    
    # Remove special characters but keep Spanish accents
    text = re.sub(r'[^a-záéíóúüñ\s.,!?]', '', text)
    
    # Ensure proper spacing after punctuation
    text = re.sub(r'\s*([.,!?])\s*', r'\1 ', text)
    
    return text.strip()

def normalize_spanish_text(text):
    """
    Normalize Spanish text for better processing.
    - Removes accents (optional)
    - Standardizes common variations
    """
    # Replace common variations
    text = text.replace('á', 'a')
    text = text.replace('é', 'e')
    text = text.replace('í', 'i')
    text = text.replace('ó', 'o')
    text = text.replace('ú', 'u')
    text = text.replace('ü', 'u')
    text = text.replace('ñ', 'n')
    
    return text

def split_spanish_sentences(text):
    """
    Split Spanish text into sentences.
    Handles common Spanish sentence endings and abbreviations.
    """
    # Add space after sentence endings if not present
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Clean up each sentence
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences 