"""ChromaDB vector store indexer with a local (offline, free) embedding model."""

import logging
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    TOP_K_RESULTS,
)
from models.schemas import DocumentChunk

logger = logging.getLogger(__name__)


class VectorIndexer:
    """Manages ChromaDB vector store for document chunks."""

    def __init__(self, persist_path: str = CHROMA_DB_PATH, collection_name: str = COLLECTION_NAME):
        """Initialize ChromaDB client and collection.

        Args:
            persist_path: Directory path for ChromaDB persistence
            collection_name: Name of the ChromaDB collection
        """
        self.persist_path = persist_path
        self.collection_name = collection_name

        # Local ONNX MiniLM embedding function — offline, free, no rate limits.
        # Same function serves both documents and queries (no task-type split needed).
        self._embedding_fn = DefaultEmbeddingFunction()

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"VectorIndexer initialized: collection='{collection_name}', docs={self.collection.count()}")
    
    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Add document chunks to the vector store.
        
        Args:
            chunks: List of DocumentChunk objects to index
        
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            documents.append(chunk.content)
            metadatas.append({
                "source_doc": chunk.source_doc,
                "section_title": chunk.section_title or "",
                "page_number": chunk.page_number or 0,
                "doc_title": chunk.metadata.title or "",
                "effective_date": chunk.metadata.effective_date or "",
                "doc_id": chunk.metadata.doc_id or "",
                "version": chunk.metadata.version or "",
                "doc_type": chunk.metadata.doc_type or "",
            })
            ids.append(chunk.chunk_id)
        
        # Upsert to handle re-indexing the same document
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Indexed {len(chunks)} chunks from '{chunks[0].source_doc}'. Total docs: {self.collection.count()}")
        return len(chunks)
    
    def search(self, query: str, top_k: int = TOP_K_RESULTS, filters: dict | None = None) -> dict:
        """Search the vector store for relevant chunks.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (ChromaDB where clause)
        
        Returns:
            ChromaDB query results dict with 'documents', 'metadatas', 'ids', 'distances'
        """
        query_embedding = self._embedding_fn([query])
        
        search_params = {
            "query_embeddings": query_embedding,
            "n_results": min(top_k, self.collection.count()) if self.collection.count() > 0 else top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if filters:
            search_params["where"] = filters
        
        try:
            results = self.collection.query(**search_params)
            logger.info(f"Search for '{query[:50]}...' returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
    
    def get_all_docs(self) -> list[str]:
        """Get list of all unique source documents in the collection."""
        if self.collection.count() == 0:
            return []
        all_data = self.collection.get(include=["metadatas"])
        sources = set()
        for meta in all_data["metadatas"]:
            if meta.get("source_doc"):
                sources.add(meta["source_doc"])
        return sorted(sources)
    
    def get_doc_count(self) -> int:
        """Get total number of chunks in the collection."""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection (for reset/testing)."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Collection '{self.collection_name}' deleted and recreated")
