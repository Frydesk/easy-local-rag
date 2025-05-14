import re
from text.spanish import clean_spanish_text, normalize_spanish_text, split_spanish_sentences

def spanish_cleaner(text):
    """
    Main cleaner for Spanish text.
    Applies all Spanish text processing steps.
    """
    # First clean the text
    text = clean_spanish_text(text)
    
    # Then normalize it
    text = normalize_spanish_text(text)
    
    # Split into sentences
    sentences = split_spanish_sentences(text)
    
    # Join sentences back with proper spacing
    return ' '.join(sentences)

def spanish_cleaner_with_accents(text):
    """
    Spanish cleaner that preserves accents.
    """
    # Clean text but preserve accents
    text = clean_spanish_text(text)
    
    # Split into sentences
    sentences = split_spanish_sentences(text)
    
    # Join sentences back with proper spacing
    return ' '.join(sentences)