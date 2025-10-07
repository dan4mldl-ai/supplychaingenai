import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import uuid

# Load environment variables
load_dotenv()

class RAGHandler:
    def __init__(self, mock=False, api_key=None, embedding_model='all-MiniLM-L6-v2'):
        # Initialize the embedding model
        self.model = SentenceTransformer(embedding_model)
        self.mock = mock
        
        # Initialize mock vectors if in mock mode
        if self.mock:
            self.mock_vectors = []
            self.index = None
            print("Running in mock mode – Pinecone disabled")
            self._initialize_mock_data()
        else:
            # Ensure API key is provided
            api_key = api_key or os.environ.get("PINECONE_API_KEY")
            env = os.environ.get("PINECONE_ENVIRONMENT")
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY is required")
            
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=api_key)

            # Check or create an index
            index_name = "scm-documents"
            dimension = 384  # Dimension for all-MiniLM-L6-v2 model
            
            # Check if index exists
            try:
                from pinecone import ServerlessSpec
                
                indexes = self.pc.list_indexes().names()
                if index_name not in indexes:
                    print(f"Creating new Pinecone index: {index_name}")
                    self.pc.create_index(
                        name=index_name,
                        dimension=dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    # Wait for index to be ready
                    import time
                    print("Waiting for index to be ready...")
                    time.sleep(10)
                    
                self.index = self.pc.Index(index_name)
                print(f"Connected to Pinecone index: {index_name}")
            except Exception as e:
                print(f"Error with Pinecone: {str(e)}")
                # Fallback to mock mode if Pinecone fails
                self.mock = True
                self.mock_vectors = []
                self._initialize_mock_data()

    
    def _initialize_mock_data(self):
        """Initialize mock data for RAG."""
        mock_documents = [
            {
                "id": "doc1",
                "text": "Supply chain management (SCM) is the management of the flow of goods and services between businesses and locations. This includes the movement and storage of raw materials, work-in-process inventory, finished goods, and end-to-end order fulfillment from the point of origin to the point of consumption.",
                "metadata": {"type": "definition", "topic": "supply chain"}
            },
            {
                "id": "doc2",
                "text": "ABC Analysis is an inventory categorization method which consists of dividing items into three categories: A, B, and C. A items are the most valuable items, B items are the interclass items, and C items are the least valuable ones.",
                "metadata": {"type": "definition", "topic": "inventory management"}
            },
            {
                "id": "doc3",
                "text": "Just-in-Time (JIT) inventory management is a strategy that aligns raw-material orders from suppliers directly with production schedules. Companies employ this inventory strategy to increase efficiency and decrease waste by receiving goods only as they need them for the production process, which reduces inventory costs.",
                "metadata": {"type": "definition", "topic": "inventory management"}
            },
            {
                "id": "doc4",
                "text": "Economic Order Quantity (EOQ) is the order quantity that minimizes the total holding costs and ordering costs. It is one of the oldest classical production scheduling models. The model was developed by Ford W. Harris in 1913, but R. H. Wilson is credited for his in-depth analysis of the model.",
                "metadata": {"type": "definition", "topic": "inventory management"}
            },
            {
                "id": "doc5",
                "text": "First-In, First-Out (FIFO) is an asset-management and valuation method in which assets produced or acquired first are sold, used, or disposed of first. For tax purposes, FIFO assumes that assets with the oldest costs are included in the income statement's cost of goods sold (COGS).",
                "metadata": {"type": "definition", "topic": "inventory management"}
            },
            {
                "id": "doc6",
                "text": "Safety stock is a term used by logisticians to describe a level of extra stock that is maintained to mitigate risk of stockouts caused by uncertainties in supply and demand. Adequate safety stock levels permit business operations to proceed according to their plans.",
                "metadata": {"type": "definition", "topic": "inventory management"}
            },
            {
                "id": "doc7",
                "text": "Order fulfillment is the complete process from point of sales inquiry to delivery of a product to the customer. Sometimes order fulfillment is used to describe the narrower act of distribution or the logistics function, however, in the broader sense it refers to the way firms respond to customer orders.",
                "metadata": {"type": "definition", "topic": "order management"}
            },
            {
                "id": "doc8",
                "text": "Supply chain analytics is the application of mathematics, statistics, predictive modeling and machine-learning techniques to find meaningful patterns and knowledge in order, shipment and transactional and sensor data.",
                "metadata": {"type": "definition", "topic": "analytics"}
            },
            {
                "id": "doc9",
                "text": "Supplier relationship management (SRM) is the systematic approach of assessing suppliers' contributions and influence on success, determining tactics to maximize suppliers' performance and developing the strategic approach for executing on these determinations.",
                "metadata": {"type": "definition", "topic": "supplier management"}
            },
            {
                "id": "doc10",
                "text": "Customer relationship management (CRM) is a technology for managing all your company's relationships and interactions with customers and potential customers. The goal is simple: Improve business relationships to grow your business.",
                "metadata": {"type": "definition", "topic": "customer management"}
            }
        ]
        
        for doc in mock_documents:
            vector = self.model.encode(doc["text"]).tolist()
            self.mock_vectors.append({
                "id": doc["id"],
                "vector": vector,
                "metadata": {
                    "text": doc["text"],
                    **doc["metadata"]
                }
            })
    
    def embed_text(self, text):
        """
        Embed text using the sentence transformer model.
        
        Args:
            text (str): Text to embed
            
        Returns:
            list: Embedding vector
        """
        return self.model.encode(text).tolist()
    
    def add_document(self, text, metadata=None):
        """
        Add a document to the vector database.
        
        Args:
            text (str): Document text
            metadata (dict, optional): Document metadata
            
        Returns:
            str: Document ID
        """
        doc_id = str(uuid.uuid4())
        vector = self.embed_text(text)
        
        if metadata is None:
            metadata = {}
        
        metadata["text"] = text
        
        if not self.mock:
            self.index.upsert([(doc_id, vector, metadata)])
        else:
            self.mock_vectors.append({
                "id": doc_id,
                "vector": vector,
                "metadata": metadata
            })
        
        return doc_id
    
    def search(self, query, top_k=5):
        """
        Search for similar documents.
        
        Args:
            query (str): Search query
            top_k (int, optional): Number of results to return
            
        Returns:
            list: Similar documents
        """
        query_vector = self.embed_text(query)
        
        if not self.mock:
            try:
                results = self.index.query(
                    vector=query_vector,
                    top_k=top_k,
                    include_metadata=True
                )
                
                # Handle the new Pinecone response format
                matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
                
                return [
                    {
                        "id": match.id if hasattr(match, 'id') else match.get('id', ''),
                        "score": match.score if hasattr(match, 'score') else match.get('score', 0),
                        "metadata": match.metadata if hasattr(match, 'metadata') else match.get('metadata', {})
                    }
                    for match in matches
                ]
            except Exception as e:
                print(f"Error querying Pinecone: {str(e)}")
                # Fall back to mock search if Pinecone query fails
                return self._mock_search(query_vector, top_k)
        else:
            return self._mock_search(query_vector, top_k)
            
    def _mock_search(self, query_vector, top_k=5):
        """
        Perform a mock search using cosine similarity.
        
        Args:
            query_vector (list): Query embedding vector
            top_k (int): Number of results to return
            
        Returns:
            list: Similar documents
        """
        # Calculate cosine similarity
        similarities = []
        
        for doc in self.mock_vectors:
            similarity = self._cosine_similarity(query_vector, doc["vector"])
            similarities.append((doc, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return [
            {
                "id": doc["id"],
                "score": score,
                "metadata": doc["metadata"]
            }
            for doc, score in similarities[:top_k]
            ]
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        return dot_product / (norm_vec1 * norm_vec2)
    
    def delete_document(self, doc_id):
        """
        Delete a document from the vector database.
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            bool: Success or failure
        """
        if not self.mock:
            self.index.delete(ids=[doc_id])
        else:
            self.mock_vectors = [doc for doc in self.mock_vectors if doc["id"] != doc_id]
        
        return True
    
    def get_answer(self, query):
        """
        Get an answer to a query using RAG.
        
        Args:
            query (str): Query
            
        Returns:
            dict: Answer with sources
        """
        # Search for relevant documents
        results = self.search(query, top_k=3)
        
        if not results:
            return {
                "answer": "I don't have enough information to answer that question.",
                "sources": []
            }
        
        # Construct context from results
        context = "\n\n".join([result["text"] for result in results])
        
        # Generate a simple answer based on the context
        # In a real implementation, this would use an LLM like OpenAI's GPT
        answer = self._generate_mock_answer(query, context, results)
        
        return {
            "answer": answer,
            "sources": results
        }
    
    def _generate_mock_answer(self, query, context, results):
        """Generate a mock answer based on the context."""
        query_lower = query.lower()
        
        # Check for specific query types
        if "abc analysis" in query_lower:
            return results[0]["text"] if any("abc analysis" in result["text"].lower() for result in results) else "ABC Analysis is an inventory categorization method which consists of dividing items into three categories: A, B, and C based on their value and sales frequency."
        
        if "jit" in query_lower or "just in time" in query_lower:
            return results[0]["text"] if any("jit" in result["text"].lower() or "just-in-time" in result["text"].lower() for result in results) else "Just-in-Time (JIT) inventory management is a strategy that aligns raw-material orders from suppliers directly with production schedules to reduce waste and inventory costs."
        
        if "eoq" in query_lower or "economic order quantity" in query_lower:
            return results[0]["text"] if any("eoq" in result["text"].lower() or "economic order quantity" in result["text"].lower() for result in results) else "Economic Order Quantity (EOQ) is the order quantity that minimizes the total holding costs and ordering costs."
        
        if "fifo" in query_lower or "first in first out" in query_lower:
            return results[0]["text"] if any("fifo" in result["text"].lower() or "first-in, first-out" in result["text"].lower() for result in results) else "First-In, First-Out (FIFO) is an asset-management method in which assets produced or acquired first are sold, used, or disposed of first."
        
        if "safety stock" in query_lower:
            return results[0]["text"] if any("safety stock" in result["text"].lower() for result in results) else "Safety stock is a level of extra stock that is maintained to mitigate risk of stockouts caused by uncertainties in supply and demand."
        
        # Default response based on the most relevant result
        return results[0]["text"] if results else "I don't have enough information to answer that question."
    
    def get_all_documents(self):
        """
        Retrieve all uploaded documents from Pinecone index.
        
        Returns:
            list: List of document metadata
        """
        if not self.mock and self.index:
            try:
                # Get index statistics to check if there are any vectors
                stats = self.index.describe_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                
                if total_vectors == 0:
                    return []
                
                # Query with a dummy vector to get all documents
                # This is a workaround since Pinecone doesn't have a direct "list all" method
                dummy_vector = [0.0] * 384  # Match the embedding dimension
                
                # Query with a high top_k to get all documents
                results = self.index.query(
                    vector=dummy_vector,
                    top_k=min(total_vectors, 10000),  # Limit to prevent excessive results
                    include_metadata=True
                )
                
                documents = []
                matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
                
                for match in matches:
                    metadata = match.metadata if hasattr(match, 'metadata') else match.get('metadata', {})
                    doc_id = match.id if hasattr(match, 'id') else match.get('id', '')
                    
                    # Extract document information from metadata
                    doc_info = {
                        "id": doc_id,
                        "name": metadata.get('file_name', 'Unknown Document'),
                        "type": metadata.get('file_type', 'Unknown'),
                        "uploaded": metadata.get('upload_date', 'Unknown'),
                        "size": metadata.get('file_size', 'Unknown'),
                        "text_preview": metadata.get('text', '')[:100] + "..." if metadata.get('text', '') else ""
                    }
                    documents.append(doc_info)
                
                # Remove duplicates based on file name
                seen_names = set()
                unique_documents = []
                for doc in documents:
                    if doc['name'] not in seen_names:
                        seen_names.add(doc['name'])
                        unique_documents.append(doc)
                
                return unique_documents
                
            except Exception as e:
                print(f"Error retrieving documents from Pinecone: {str(e)}")
                return []
        else:
            # Return mock documents if not using Pinecone
            return [
                {
                    "id": "mock_1",
                    "name": "Sample Document.pdf",
                    "type": "PDF",
                    "uploaded": "2023-07-10",
                    "size": "1.2 MB",
                    "text_preview": "This is a sample document for testing purposes..."
                }
            ]