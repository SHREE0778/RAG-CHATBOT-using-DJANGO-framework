import logging
import os
import requests
import json
import time

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern - ensures only one service instance exists.
        Switched to HuggingFace API to avoid OOM on Free Tier.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
            cls._instance.api_token = os.environ.get('HF_TOKEN')
            
            if not cls._instance.api_token:
                logger.warning("⚠️ HF_TOKEN not found! Embedding service will fail unless token is provided.")
            
            logger.info(f"✅ Embedding API Service initialized (Model: all-MiniLM-L6-v2)")
        
        return cls._instance
    
    def _query_api(self, payload):
        """Helper to query HF API with retries"""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        # Simple retry logic for "model loading" or rate limits
        for i in range(3):
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.json()
            
            # If model is loading, wait and retry
            if "estimated_time" in response.text:
                wait_time = response.json().get("estimated_time", 5)
                logger.info(f"Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            logger.error(f"HF API Error: {response.status_code} - {response.text}")
            break
            
        return None

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts using API"""
        if not texts or not self.api_token:
            return []
            
        try:
            # HF API expects list of strings
            output = self._query_api({"inputs": texts, "options": {"wait_for_model": True}})
            
            if isinstance(output, list) and len(output) > 0:
                # Check if it returned a list of lists (embeddings)
                if isinstance(output[0], list):
                    return output
                # Sometimes it returns slightly different format depending on pipeline
                # all-MiniLM-L6-v2 features-extraction returns list of lists
                
            return []
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text"""
        embeddings = self.generate_embeddings([text])
        if embeddings:
            return embeddings[0]
        return []

    def get_model_info(self):
        return {
            'model_name': 'all-MiniLM-L6-v2 (API)',
            'mode': 'Refactored for 512MB RAM'
        }