import chromadb
from typing import List, Dict
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        try:
            self.client = chromadb.PersistentClient(
                path=str(settings.CHROMA_PERSIST_DIRECTORY)
            )
            self.collection_name = f"user_{user_id}_docs"
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"Vector store initialized for user {user_id}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, texts: List[str], embeddings: List[List[float]], 
                     metadatas: List[Dict] = None):
        """Add documents to the vector store"""
        try:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas or [{}] * len(texts),
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, query_embedding: List[float], n_results: int = 3):
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def delete_collection(self):
        """Delete user's collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")