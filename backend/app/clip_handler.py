"""
Text Embedding Handler
Handles loading and inference of text embedding models.
"""

import logging
from typing import List, Union

import torch
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class CLIPHandler:
    """Handler for text embedding operations."""

    def __init__(self, text_model_name: str = "sentence-transformers/clip-ViT-B-32-multilingual-v1"):
        """
        Initialize text embedding handler.

        Args:
            text_model_name: Name of the Multilingual CLIP model (for text)
        """
        self.text_model_name = text_model_name
        self.text_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self):
        """Load the text embedding model."""
        try:
            logger.info(f"Loading Multilingual text embedding model: {self.text_model_name}")
            self.text_model = SentenceTransformer(self.text_model_name, device=self.device)
            logger.info("✅ Text embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load text embedding model: {e}")
            raise

    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Encode text into embeddings using Multilingual CLIP.

        Args:
            text: Single text string or list of text strings

        Returns:
            Normalized embedding vector(s)
        """
        if self.text_model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Generate embeddings (SentenceTransformer outputs normalized embeddings by default)
            embeddings = self.text_model.encode(text, convert_to_numpy=True)

            return embeddings

        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode a batch of texts.

        Args:
            texts: List of text strings

        Returns:
            Text embeddings array
        """
        return self.encode_text(texts)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.

        Returns:
            Embedding dimension
        """
        if self.text_model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        return self.text_model.get_sentence_embedding_dimension()
