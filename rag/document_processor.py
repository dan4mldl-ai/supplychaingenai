import os
import uuid
from typing import List, Dict, Any, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

from rag.rag_handler import RAGHandler

class DocumentProcessor:
    """
    Processes documents for RAG system, including text extraction, chunking, and embedding.
    """
    
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the document processor.
        
        Args:
            embedding_model (str): Name of the sentence transformer model to use
        """
        # Prefer CPU to avoid PyTorch meta device issues
        device = 'cuda' if hasattr(torch, 'cuda') and torch.cuda.is_available() else 'cpu'
        try:
            self.model = SentenceTransformer(embedding_model, device=device)
        except NotImplementedError as e:
            # Fallback to CPU in case of meta tensor/device errors
            print(f"SentenceTransformer init error ({e}); falling back to CPU.")
            self.model = SentenceTransformer(embedding_model, device='cpu')
        self.supported_extensions = ['.txt', '.csv', '.pdf', '.docx', '.xlsx']
        # Safety limits to avoid memory issues
        self.max_text_chars = int(os.environ.get("MAX_TEXT_CHARS", "1000000"))  # 1M chars
        self.max_chunks = int(os.environ.get("MAX_CHUNKS", "5000"))
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if the file type is supported.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if supported, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.supported_extensions
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Extracted text
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Mock implementation for different file types
        if ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    # Cap text to avoid huge memory usage
                    return text[:self.max_text_chars]
            except Exception as e:
                print(f"Error reading text file: {e}")
                return ""
        
        elif ext == '.csv':
            try:
                # Limit rows to avoid huge string generation
                df = pd.read_csv(file_path)
                text = df.head(1000).to_string()
                return text[:self.max_text_chars]
            except Exception as e:
                print(f"Error reading CSV file: {e}")
                return ""
        
        # For other file types, return mock data
        elif ext == '.pdf':
            return f"Mock PDF content from {os.path.basename(file_path)}"
        
        elif ext == '.docx':
            return f"Mock DOCX content from {os.path.basename(file_path)}"
        
        elif ext == '.xlsx':
            return f"Mock Excel content from {os.path.basename(file_path)}"
        
        else:
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text (str): Text to chunk
            chunk_size (int): Maximum size of each chunk
            overlap (int): Overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
        
        # Simple chunking by characters with overlap
        # Ensure overlap < chunk_size to avoid infinite loops
        if overlap >= chunk_size:
            overlap = max(0, chunk_size // 2)
        chunks = []
        start = 0
        
        count = 0
        while start < len(text) and count < self.max_chunks:
            end = min(start + chunk_size, len(text))
            
            # Try to find a good breaking point (newline or space)
            if end < len(text):
                # Look for newline first
                newline_pos = text.rfind('\n', start, end)
                if newline_pos > start:
                    end = newline_pos + 1
                else:
                    # Look for space
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos + 1
            
            # Guard against no progress
            if end <= start:
                break
            chunks.append(text[start:end])
            start = end - overlap
            count += 1
        
        return chunks
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Embed text chunks.
        
        Args:
            chunks (List[str]): List of text chunks
            
        Returns:
            List[List[float]]: List of embeddings
        """
        if not chunks:
            return []
        
        # Use batched encoding to reduce memory spikes
        try:
            return self.model.encode(chunks, batch_size=32).tolist()
        except Exception:
            # Fallback to per-chunk encoding
            return [self.model.encode(chunk).tolist() for chunk in chunks]
    
    def process_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process a document: extract text, chunk, and embed.
        
        Args:
            file_path (str): Path to the document
            metadata (Dict[str, Any], optional): Additional metadata
            
        Returns:
            List[Dict[str, Any]]: List of processed chunks with embeddings and metadata
        """
        if not self.is_supported_file(file_path):
            return []
        
        # Extract text
        text = self.extract_text(file_path)
        if not text:
            return []
        
        # Chunk text
        chunks = self.chunk_text(text)
        
        # Embed chunks
        embeddings = self.embed_chunks(chunks)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": os.path.splitext(file_path)[1].lower()
        })
        
        # Create document chunks
        document_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            document_chunks.append({
                "id": chunk_id,
                "text": chunk,
                "embedding": embedding,
                "metadata": {
                    **metadata,
                    "chunk_index": i
                }
            })
        
        return document_chunks