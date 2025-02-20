from typing import List, Dict, Any
from models.base import Document, Dataset
from services.llm import LLMService
import json

class RAGService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def process_document(self, document: Document) -> None:
        """Process a document and store its embeddings"""
        # Split document into chunks
        chunks = self.llm_service.process_document(document.content)
        
        # Create embeddings for chunks
        embeddings = self.llm_service.create_embeddings([chunk.page_content for chunk in chunks])
        
        # Store embeddings in document metadata
        document.metadata = {
            'chunks': [
                {
                    'content': chunk.page_content,
                    'embedding': embedding.tolist(),
                    'metadata': chunk.metadata
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]
        }
    
    def query_dataset(self, dataset: Dataset, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query a dataset for relevant documents"""
        # Create query embedding
        query_embedding = self.llm_service.create_embeddings([query])[0]
        
        results = []
        for document in dataset.documents:
            if not document.metadata:
                continue
                
            chunks = document.metadata.get('chunks', [])
            for chunk in chunks:
                similarity = self._compute_similarity(
                    query_embedding,
                    chunk['embedding']
                )
                results.append({
                    'document_id': document.id,
                    'chunk_content': chunk['content'],
                    'similarity': similarity,
                    'metadata': chunk['metadata']
                })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]
    
    def _compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        import numpy as np
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
