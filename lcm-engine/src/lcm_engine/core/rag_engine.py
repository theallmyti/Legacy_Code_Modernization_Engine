import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class RAGEngine:
    """
    RAG Engine using ChromaDB for Vector Storage and sentence-transformers for embeddings.
    Provides context optimization by retrieving relevant semantic chunks.
    """
    def __init__(self, db_path: str = "./.lcm_chroma_db", collection_name: str = "legacy_code"):
        # Initialize chroma client (persistent locally)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Load embedding model (all-MiniLM-L6-v2 is fast and effective for code/text)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Store code chunks into the vector database."""
        if not chunks:
            return

        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        
        # Convert metadata values to strings or basic types that Chroma allows
        metadatas = []
        for chunk in chunks:
            raw_meta = chunk.get("metadata", {})
            safe_meta = {"name": chunk["name"], "type": chunk["type"]}
            if "length" in raw_meta:
                 safe_meta["length"] = raw_meta["length"]
            # Convert dependencies to a comma-separated string
            if chunk.get("dependencies"):
                safe_meta["dependencies"] = ",".join(chunk["dependencies"])
            metadatas.append(safe_meta)
            
        # Generate embeddings
        embeddings = self.encoder.encode(documents).tolist()
        
        # Upsert into Chroma (updates if id exists, insert otherwise)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def retrieve_context(self, query: str = "", query_chunk: Dict[str, Any] = None, k: int = 3) -> List[Dict[str, Any]]:
        """
        Find related chunks for context optimization.
        Can search by string query or by a target chunk.
        """
        search_text = query
        if query_chunk and query_chunk.get("content"):
            search_text = query_chunk["content"]

        if not search_text:
            return []

        query_embedding = self.encoder.encode([search_text]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        context_chunks = []
        # Return structured format
        if results and results["documents"] and results["documents"][0]:
            for i in range(len(results["ids"][0])):
                context_chunks.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else 0.0
                })
                
        return context_chunks
