"""
Embedding models for generating vector representations of text.
Supports both OpenAI and local sentence-transformers models.
"""

import os
from typing import List, Union
from abc import ABC, abstractmethod
import numpy as np


class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Encode text(s) into embeddings."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embeddings."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name."""
        pass


class OpenAIEmbedding(EmbeddingModel):
    """OpenAI embedding model wrapper."""
    
    SUPPORTED_MODELS = {
        "text-embedding-3-large": 3072,
        "text-embedding-3-small": 1536,
        "text-embedding-ada-002": 1536
    }
    
    def __init__(self, model_name: str = "text-embedding-3-large", api_key: str = None):
        """
        Initialize OpenAI embedding model.
        
        Args:
            model_name: Name of the OpenAI model
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model_name}. Supported: {list(self.SUPPORTED_MODELS.keys())}")
        
        self._model_name = model_name
        self._dimension = self.SUPPORTED_MODELS[model_name]
        
        # Import OpenAI here to make it optional
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required. Install with: pip install openai")
        
        # Initialize client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        self.client = OpenAI(api_key=api_key)
    
    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = False) -> np.ndarray:
        """
        Encode text(s) using OpenAI API.
        
        Args:
            texts: Text or list of texts to encode
            show_progress_bar: Whether to show progress (ignored for OpenAI)
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Handle batch processing for large inputs
        embeddings = []
        batch_size = 100  # OpenAI rate limit consideration
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self._model_name,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                raise RuntimeError(f"OpenAI API error: {e}")
        
        return np.array(embeddings)
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def model_name(self) -> str:
        return self._model_name


class SentenceTransformerEmbedding(EmbeddingModel):
    """Sentence Transformers embedding model wrapper."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers package required. Install with: pip install sentence-transformers")
        
        self._model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = True) -> np.ndarray:
        """
        Encode text(s) using sentence transformers.
        
        Args:
            texts: Text or list of texts to encode
            show_progress_bar: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        return self.model.encode(texts, show_progress_bar=show_progress_bar)
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def model_name(self) -> str:
        return self._model_name


def create_embedding_model(model_name: str, **kwargs) -> EmbeddingModel:
    """
    Factory function to create embedding models.
    
    Args:
        model_name: Name of the model
        **kwargs: Additional arguments for model initialization
        
    Returns:
        EmbeddingModel instance
    """
    # OpenAI models
    if model_name in OpenAIEmbedding.SUPPORTED_MODELS:
        return OpenAIEmbedding(model_name=model_name, **kwargs)
    
    # Sentence transformer models (default)
    return SentenceTransformerEmbedding(model_name=model_name)