import re
import unicodedata
import codecs

def clean_spanish_text(text):
    """
    Clean and normalize Spanish text.
    - Removes extra whitespace
    - Normalizes punctuation
    - Handles common Spanish abbreviations
    - Preserves Spanish accents and special characters
    """
    # Ensure text is in UTF-8 BOM
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
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
    
    # Remove special characters but keep Spanish accents and ñ
    text = re.sub(r'[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s.,!?]', '', text)
    
    # Ensure proper spacing after punctuation
    text = re.sub(r'\s*([.,!?])\s*', r'\1 ', text)
    
    # Ensure output is UTF-8 BOM
    return text.strip().encode('utf-8-sig').decode('utf-8-sig')

def normalize_spanish_text(text):
    """
    Normalize Spanish text for better processing.
    - Preserves accents and special characters
    - Standardizes common variations
    """
    # Ensure text is in UTF-8 BOM
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Keep Spanish characters as is and ensure UTF-8 BOM
    return text.encode('utf-8-sig').decode('utf-8-sig')

def split_spanish_sentences(text):
    """
    Split Spanish text into sentences.
    Handles common Spanish sentence endings and abbreviations.
    """
    # Ensure text is in UTF-8 BOM
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    
    # Add space after sentence endings if not present
    text = re.sub(r'([.!?])([A-ZÁÉÍÓÚÜÑ])', r'\1 \2', text)
    
    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Clean up each sentence and ensure UTF-8 BOM
    sentences = [s.strip().encode('utf-8-sig').decode('utf-8-sig') for s in sentences if s.strip()]
    
    return sentences 