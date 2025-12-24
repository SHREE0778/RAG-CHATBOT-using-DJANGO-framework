from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    
    def __new__(cls, model_name: str = None):
        """
        Singleton pattern - ensures only one model instance exists.
        Optimized for deployment with CPU-only usage.
        """
        if cls._instance is None:
            # Lazy load heavy dependencies
            import torch
            from sentence_transformers import SentenceTransformer

            # Get model name from environment or use default
            if model_name is None:
                model_name = os.environ.get('EMBEDDING_MODEL', 'paraphrase-MiniLM-L3-v2')
            
            # Force CPU usage (critical for deployment)
            device = 'cpu'
            
            # Limit PyTorch threads to reduce memory
            torch.set_num_threads(2)
            os.environ['OMP_NUM_THREADS'] = '2'
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            
            logger.info(f"🔄 Loading embedding model: {model_name} on {device}")
            
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer(model_name, device=device)
            cls._instance.model_name = model_name
            
            logger.info(f"✅ Loaded embedding model: {model_name}")
        
        return cls._instance
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        
        # Use batch encoding with progress bar disabled for cleaner logs
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            batch_size=32  # Optimize batch size for memory
        )
        
        return embeddings.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text:
            return []
        
        embedding = self.model.encode(
            [text],
            show_progress_bar=False,
            convert_to_numpy=True
        )[0]
        
        return embedding.tolist()
    
    def get_model_info(self):
        """Return model information for debugging"""
        return {
            'model_name': self.model_name,
            'device': str(self.model.device),
            'max_seq_length': self.model.max_seq_length,
            'embedding_dimension': self.model.get_sentence_embedding_dimension()
        }