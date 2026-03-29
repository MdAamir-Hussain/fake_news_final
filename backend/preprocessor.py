"""
Text Preprocessing Pipeline
Handles cleaning, tokenization, stopword removal, and lemmatization.
"""

import re
import nltk

# Download required NLTK resources
for resource in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def clean_text(self, text: str) -> str:
        """Normalize and clean raw text."""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        # Replace URLs
        text = re.sub(r'http\S+|www\S+|https\S+', ' url ', text, flags=re.MULTILINE)
        # Replace emails
        text = re.sub(r'\S+@\S+', ' email ', text)
        # Replace phone numbers
        text = re.sub(r'\b\d[\d\s\-().]{7,}\d\b', ' phone ', text)
        # Replace standalone numbers
        text = re.sub(r'\b\d+\b', ' num ', text)
        # Remove special characters
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into word tokens."""
        try:
            return word_tokenize(text)
        except Exception:
            return text.split()

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        """Filter out stopwords and very short tokens."""
        return [t for t in tokens if t not in self.stop_words and len(t) > 2]

    def lemmatize(self, tokens: list[str]) -> list[str]:
        """Reduce tokens to their base/lemma form."""
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def preprocess(self, text: str) -> str:
        """
        Full preprocessing pipeline:
        clean → tokenize → remove stopwords → lemmatize → rejoin
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize(tokens)
        return ' '.join(tokens)

    def preprocess_batch(self, texts: list[str]) -> list[str]:
        """Preprocess a batch of texts."""
        return [self.preprocess(t) for t in texts]
