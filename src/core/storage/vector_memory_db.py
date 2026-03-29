"""Vector database for persistent agent memory (ChromaDB integration)."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class VectorMemoryDB:
    """Persistent memory using vector database."""
    
    def __init__(self, db_path: str = "./data/chroma_db"):
        """Initialize vector memory database."""
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._connect()
    
    def _connect(self):
        """Connect to ChromaDB."""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(self.db_path))
            logger.info(f"✅ Vector DB connected to {self.db_path}")
        except ImportError:
            logger.warning("⚠️ ChromaDB not installed, using memory-only fallback")
            self._client = None
            self._memory = {}
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to ChromaDB: {e}")
            self._client = None
            self._memory = {}
    
    def get_or_create_collection(self, collection_name: str):
        """Get or create collection."""
        if self._client is None:
            if collection_name not in self._memory:
                self._memory[collection_name] = {"embeddings": [], "documents": [], "metadatas": [], "ids": []}
            return self._memory[collection_name]
        
        return self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_memory(
        self,
        collection: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to memory."""
        try:
            col = self.get_or_create_collection(collection)
            
            if self._client is not None:
                col.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.debug(f"✅ Added {len(documents)} documents to {collection}")
            else:
                # Memory-only fallback
                col["documents"].extend(documents)
                col["metadatas"].extend(metadatas)
                col["ids"].extend(ids)
        except Exception as e:
            logger.error(f"❌ Error adding to memory: {e}")
    
    def query_memory(
        self,
        collection: str,
        query_texts: List[str],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query memory with semantic search."""
        try:
            col = self.get_or_create_collection(collection)
            
            if self._client is not None:
                results = col.query(
                    query_texts=query_texts,
                    n_results=n_results
                )
                return results
            else:
                # Memory-only fallback - simple search
                return {
                    "ids": [col["ids"][:n_results]],
                    "documents": [col["documents"][:n_results]],
                    "metadatas": [col["metadatas"][:n_results]],
                    "distances": [[0.0] * min(n_results, len(col["ids"]))]
                }
        except Exception as e:
            logger.error(f"❌ Error querying memory: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
    
    def get_all_memory(self, collection: str) -> Dict[str, Any]:
        """Get all documents from collection."""
        try:
            col = self.get_or_create_collection(collection)
            
            if self._client is not None:
                return col.get()
            else:
                return col
        except Exception as e:
            logger.error(f"❌ Error getting memory: {e}")
            return {"ids": [], "documents": [], "metadatas": []}
    
    def delete_memory(self, collection: str, ids: List[str]) -> None:
        """Delete documents from memory."""
        try:
            col = self.get_or_create_collection(collection)
            
            if self._client is not None:
                col.delete(ids=ids)
                logger.debug(f"✅ Deleted {len(ids)} documents from {collection}")
            else:
                # Memory-only fallback
                for id_val in ids:
                    if id_val in col["ids"]:
                        idx = col["ids"].index(id_val)
                        col["ids"].pop(idx)
                        col["documents"].pop(idx)
                        col["metadatas"].pop(idx)
        except Exception as e:
            logger.error(f"❌ Error deleting from memory: {e}")
    
    def clear_collection(self, collection: str) -> None:
        """Clear entire collection."""
        try:
            if self._client is not None:
                self._client.delete_collection(name=collection)
            else:
                if collection in self._memory:
                    del self._memory[collection]
            logger.info(f"✅ Cleared collection {collection}")
        except Exception as e:
            logger.warning(f"⚠️ Could not clear collection: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            "backend": "chromadb" if self._client else "memory",
            "db_path": str(self.db_path),
            "collections": []
        }
        
        try:
            if self._client is not None:
                collections = self._client.list_collections()
                for col in collections:
                    count = col.count()
                    stats["collections"].append({
                        "name": col.name,
                        "documents": count
                    })
            else:
                for col_name, col_data in self._memory.items():
                    stats["collections"].append({
                        "name": col_name,
                        "documents": len(col_data.get("ids", []))
                    })
        except Exception as e:
            logger.warning(f"⚠️ Could not get stats: {e}")
        
        return stats


# Global instance
_vector_db: Optional[VectorMemoryDB] = None


def get_vector_db(db_path: str = "./data/chroma_db") -> VectorMemoryDB:
    """Get or create vector database instance."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorMemoryDB(db_path)
    return _vector_db
