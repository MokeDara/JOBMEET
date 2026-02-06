"""
Text extraction and cleaning utilities
"""

import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import io

# Download NLTK data (runs once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def extract_resume_text(pdf_file) -> str:
    """
    Extract text from PDF resume file.
    
    Args:
        pdf_file: Streamlit uploaded file object
        
    Returns:
        Extracted text from PDF
    """
    try:
        pdf_bytes = pdf_file.read()
        pdf_file_obj = io.BytesIO(pdf_bytes)
        
        text = ""
        with pdfplumber.open(pdf_file_obj) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def clean_text(text: str) -> str:
    """
    Clean text by removing stop words, lowercasing, and special characters.
    Constraint: No underscores or hyphens in output summaries.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text suitable for analysis
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Rejoin
    cleaned = ' '.join(tokens)
    
    return cleaned


def extract_keywords(text: str, top_n: int = 20) -> list:
    """
    Extract top keywords from text based on frequency.
    
    Args:
        text: Cleaned text
        top_n: Number of top keywords to extract
        
    Returns:
        List of top keywords
    """
    tokens = text.split()
    
    # Count frequency
    freq_dist = {}
    for token in tokens:
        freq_dist[token] = freq_dist.get(token, 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(freq_dist.items(), key=lambda x: x[1], reverse=True)
    
    return [keyword for keyword, freq in sorted_keywords[:top_n]]
