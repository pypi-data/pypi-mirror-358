"""
Main NotionArchive class - the primary interface for the library.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .parser import NotionDocument, NotionExportParser
from .embeddings import create_embedding_model, EmbeddingModel


class NotionArchive:
    """
    Transform Notion exports into searchable knowledge bases using AI embeddings.
    
    Usage:
        archive = NotionArchive(embedding_model="text-embedding-3-large")
        archive.add_export('./my_notion_export')
        archive.build_index()
        results = archive.search("AI strategy meetings")
    """
    
    def __init__(self, 
                 embedding_model: str = "text-embedding-3-large",
                 openai_api_key: Optional[str] = None,
                 db_path: str = "./notion_archive_db",
                 collection_name: str = "documents",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize Notion Archive.
        
        Args:
            embedding_model: Model name ("text-embedding-3-large", "all-MiniLM-L6-v2", etc.)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            db_path: Path to store the vector database
            collection_name: Name of the document collection
            chunk_size: Maximum size of document chunks
            chunk_overlap: Overlap between document chunks
        """
        self.embedding_model_name = embedding_model
        self.db_path = db_path
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding model
        self.embedding_model: EmbeddingModel = create_embedding_model(
            embedding_model, 
            api_key=openai_api_key
        )
        
        # Initialize ChromaDB
        self._init_database()
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Store parsed documents before indexing
        self.documents: List[NotionDocument] = []
    
    def _init_database(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
        except Exception as e:
            print(f"Warning: ChromaDB initialization issue: {e}")
            self.client = chromadb.Client()
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Notion Archive documents"}
                )
                print(f"Created new collection: {self.collection_name}")
            except Exception as e:
                print(f"Error creating collection: {e}")
                raise
    
    def add_export(self, export_path: str) -> None:
        """
        Add a Notion export to the archive.
        
        Args:
            export_path: Path to the Notion export folder
        """
        export_path = Path(export_path).resolve()  # Resolve to absolute path
        
        if not export_path.exists():
            raise ValueError(f"Export path does not exist: {export_path}")
        
        if not export_path.is_dir():
            raise ValueError(f"Export path must be a directory: {export_path}")
        
        print(f"Parsing Notion export: {export_path}")
        parser = NotionExportParser(export_path)
        new_documents = parser.parse_export()
        
        if not new_documents:
            print(f"No documents found in {export_path}")
            return
        
        self.documents.extend(new_documents)
        print(f"Added {len(new_documents)} documents from {export_path}")
    
    def has_index(self) -> bool:
        """
        Check if the archive already has an index built.
        
        Returns:
            True if index exists, False otherwise
        """
        try:
            return self.collection.count() > 0
        except:
            return False
    
    def build_index(self, show_progress: bool = True, force_rebuild: bool = False) -> None:
        """
        Build the search index by generating embeddings for all documents.
        This is the computationally expensive step that should be run once.
        
        Args:
            show_progress: Whether to show progress indicators
            force_rebuild: If True, rebuild even if index already exists
        """
        # Check if index already exists
        try:
            existing_count = self.collection.count()
            if existing_count > 0 and not force_rebuild:
                print(f"Index already exists with {existing_count} documents.")
                print("Use force_rebuild=True to rebuild, or skip this call to use existing index.")
                return
        except Exception as e:
            print(f"Warning checking existing data: {e}")
        
        if not self.documents:
            raise ValueError("No documents to index. Call add_export() first.")
        
        # Warn about large workspaces
        if len(self.documents) > 1000:
            print(f"⚠️  Warning: Large workspace with {len(self.documents)} documents")
            print("   This may take a long time and cost significant money with OpenAI models")
        
        print(f"Building index for {len(self.documents)} documents...")
        print(f"Using embedding model: {self.embedding_model.model_name}")
        
        # Clear existing collection if rebuilding
        try:
            existing_count = self.collection.count()
            if existing_count > 0:
                print(f"Clearing existing {existing_count} documents...")
                self.collection.delete()
        except Exception as e:
            print(f"Warning clearing collection: {e}")
        
        # Process documents into chunks
        texts = []
        metadatas = []
        ids = []
        
        for doc in self.documents:
            if len(doc.plain_text) > self.chunk_size:
                # Split large documents into chunks
                chunks = self.text_splitter.split_text(doc.plain_text)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc.id}_chunk_{i}"
                    ids.append(chunk_id)
                    texts.append(chunk)
                    
                    metadata = {
                        "original_id": doc.id,
                        "title": doc.title,
                        "workspace": doc.workspace,
                        "url_path": doc.url_path,
                        "breadcrumb": " > ".join(doc.breadcrumb),
                        "tags": ", ".join(doc.tags),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "created_by": doc.created_by or "",
                        "last_edited_by": doc.last_edited_by or "",
                        "created_time": doc.created_time.isoformat() if doc.created_time else "",
                        "last_edited_time": doc.last_edited_time.isoformat() if doc.last_edited_time else ""
                    }
                    metadatas.append(metadata)
            else:
                # Use whole document
                ids.append(doc.id)
                texts.append(doc.plain_text)
                
                metadata = {
                    "original_id": doc.id,
                    "title": doc.title,
                    "workspace": doc.workspace,
                    "url_path": doc.url_path,
                    "breadcrumb": " > ".join(doc.breadcrumb),
                    "tags": ", ".join(doc.tags),
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "created_by": doc.created_by or "",
                    "last_edited_by": doc.last_edited_by or "",
                    "created_time": doc.created_time.isoformat() if doc.created_time else "",
                    "last_edited_time": doc.last_edited_time.isoformat() if doc.last_edited_time else ""
                }
                metadatas.append(metadata)
        
        # Filter out empty texts
        filtered_data = [(text, meta, id_) for text, meta, id_ in zip(texts, metadatas, ids) if text.strip()]
        if not filtered_data:
            raise ValueError("No valid text content found in documents")
        
        texts, metadatas, ids = zip(*filtered_data)
        texts, metadatas, ids = list(texts), list(metadatas), list(ids)
        
        # Generate embeddings
        print("Generating embeddings...")
        
        # Cost warning for OpenAI models
        if "text-embedding" in self.embedding_model.model_name:
            total_tokens = sum(len(text.split()) for text in texts)
            estimated_cost = total_tokens * 0.00001  # Rough estimate
            if estimated_cost > 1.0:
                print(f"⚠️  Warning: Estimated OpenAI cost ~${estimated_cost:.2f}")
                print(f"   Processing {len(texts)} chunks, ~{total_tokens} tokens")
        
        embeddings = self.embedding_model.encode(texts, show_progress_bar=show_progress)
        
        # Add to ChromaDB
        print("Storing in vector database...")
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            
            try:
                self.collection.add(
                    documents=texts[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    embeddings=embeddings_list[i:batch_end],
                    ids=ids[i:batch_end]
                )
            except Exception as e:
                print(f"Error adding batch {i}-{batch_end}: {e}")
                continue
        
        print(f"Successfully indexed {len(texts)} chunks from {len(self.documents)} documents")
    
    def search(self, 
               query: str, 
               limit: int = 10,
               workspace: Optional[str] = None,
               tags: Optional[List[str]] = None,
               **filters) -> List[Dict[str, Any]]:
        """
        Search the archive using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            workspace: Filter by workspace name
            tags: Filter by tags (must contain ALL specified tags)
            **filters: Additional metadata filters
            
        Returns:
            List of search results with content and metadata
        """
        # Build where clause for filtering
        where_clause = {}
        if workspace:
            where_clause["workspace"] = workspace
        if tags:
            for tag in tags:
                where_clause["tags"] = {"$contains": tag}
        where_clause.update(filters)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=limit,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"Search error: {e}")
            return []
        
        # Format results
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            for i in range(len(results["documents"][0])):
                # Convert distance to similarity score (0-1, higher is better)
                distance = results["distances"][0][i]
                score = max(0, 1 - distance)
                
                result = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": score,
                    "title": results["metadatas"][0][i].get("title", ""),
                    "workspace": results["metadatas"][0][i].get("workspace", ""),
                    "tags": [tag.strip() for tag in results["metadatas"][0][i].get("tags", "").split(",") if tag.strip()],
                    "breadcrumb": results["metadatas"][0][i].get("breadcrumb", "").split(" > "),
                    "url": results["metadatas"][0][i].get("url_path", "")
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed archive."""
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze
            sample_results = self.collection.get(limit=min(100, count))
            
            workspaces = set()
            tags = set()
            
            for metadata in sample_results.get("metadatas", []):
                if metadata.get("workspace"):
                    workspaces.add(metadata["workspace"])
                if metadata.get("tags"):
                    tags.update([tag.strip() for tag in metadata["tags"].split(",") if tag.strip()])
            
            return {
                "total_documents": len(self.documents),
                "total_chunks": count,
                "workspaces": sorted(list(workspaces)),
                "tags": sorted(list(tags)),
                "embedding_model": self.embedding_model.model_name,
                "embedding_dimension": self.embedding_model.dimension
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": len(self.documents),
                "total_chunks": 0,
                "workspaces": [],
                "tags": []
            }
    
    def clear_index(self) -> None:
        """Clear the search index."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Notion Archive documents"}
            )
            print("Index cleared successfully")
        except Exception as e:
            print(f"Error clearing index: {e}")