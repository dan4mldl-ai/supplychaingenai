from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from rag.rag_handler import RAGHandler

import os

class QueryEngine:
    """
    Handles query processing and retrieval for the RAG system.
    """
    
    def __init__(self, rag_handler: Optional[RAGHandler] = None, embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the query engine.
        
        Args:
            rag_handler (RAGHandler, optional): RAG handler instance
            embedding_model (str): Name of the sentence transformer model to use
        """
        #self.rag_handler = rag_handler or RAGHandler(mock=False)  # Use actual Pinecone instead of mock
        self.rag_handler = rag_handler or RAGHandler(mock=False,api_key=os.environ.get("PINECONE_API_KEY"))

        # Prefer CPU to avoid PyTorch meta device issues
        device = 'cuda' if hasattr(torch, 'cuda') and torch.cuda.is_available() else 'cpu'
        try:
            self.model = SentenceTransformer(embedding_model, device=device)
        except NotImplementedError as e:
            # Fallback to CPU in case of meta tensor/device errors
            print(f"SentenceTransformer init error ({e}); falling back to CPU.")
            self.model = SentenceTransformer(embedding_model, device='cpu')
    
    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Process a query and retrieve relevant documents.
        
        Args:
            query (str): User query
            top_k (int): Number of results to return
            
        Returns:
            Dict[str, Any]: Query results with answer and sources
        """
        # Search for relevant documents
        relevant_docs = self.search_documents(query, top_k)
        
        # If we have actual documents from Pinecone, use them
        if relevant_docs and not self.rag_handler.mock:
            return self._generate_response_from_docs(query, relevant_docs)
        else:
            # Fall back to RAG handler's answer if no documents found
            return self.rag_handler.get_answer(query)
            
    def _generate_response_from_docs(self, query: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response based on retrieved documents.
        
        Args:
            query (str): User query
            docs (List[Dict[str, Any]]): Retrieved documents
            
        Returns:
            Dict[str, Any]: Response with answer and sources
        """
        # Extract text from documents
        contexts = []
        for doc in docs:
            if "metadata" in doc:
                metadata = doc["metadata"]
                if isinstance(metadata, dict) and "text" in metadata:
                    contexts.append(metadata["text"])
        
        # Extract source information
        sources = []
        for doc in docs:
            if "metadata" in doc:
                metadata = doc["metadata"]
                if isinstance(metadata, dict) and "file_name" in metadata:
                    sources.append({
                        "file_name": metadata["file_name"],
                        "relevance": doc.get("score", 0)
                    })
        
        # Generate response based on the query and context
        answer = self.generate_response(query, contexts)
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents relevant to the query.
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: Relevant documents
        """
        return self.rag_handler.search(query, top_k=top_k)
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generate a response based on the query and context.
        
        Args:
            query (str): User query
            context (List[str]): Context from retrieved documents
            
        Returns:
            str: Generated response
        """
        # In a real implementation, this would use an LLM like OpenAI's GPT
        # For now, we'll use the context directly from Pinecone
        
        if not context:
            return "I couldn't find any relevant information in the uploaded documents."
            
        # Combine the context information to form a response
        response = f"Based on the uploaded documents, here's information about '{query}':\n\n"
        
        # Add unique contexts to the response (avoid duplicates)
        unique_contexts = list(set(context))
        for i, ctx in enumerate(unique_contexts[:3]):
            # Limit context length for readability
            ctx_preview = ctx[:300] + "..." if len(ctx) > 300 else ctx
            response += f"Document {i+1}: {ctx_preview}\n\n"
            
        return response
        
        # Join context
        context_text = "\n\n".join(context)
        
        # Generate mock response based on query keywords
        query_lower = query.lower()
        
        if "inventory" in query_lower:
            if "abc" in query_lower:
                return "ABC Analysis is an inventory categorization method which consists of dividing items into three categories: A, B, and C based on their value and sales frequency. Category A items are the most valuable and require close monitoring, B items are moderately valuable, and C items are least valuable but may represent the bulk of inventory items."
            elif "jit" in query_lower or "just in time" in query_lower:
                return "Just-in-Time (JIT) inventory management is a strategy that aligns raw-material orders from suppliers directly with production schedules. Companies employ this inventory strategy to increase efficiency and decrease waste by receiving goods only as they need them for the production process, which reduces inventory costs."
            elif "eoq" in query_lower:
                return "Economic Order Quantity (EOQ) is the order quantity that minimizes the total holding costs and ordering costs. The formula is EOQ = sqrt(2DS/H), where D is annual demand, S is order cost, and H is annual holding cost per unit."
            elif "safety stock" in query_lower:
                return "Safety stock is a term used by logisticians to describe a level of extra stock that is maintained to mitigate risk of stockouts caused by uncertainties in supply and demand. It's calculated based on factors like lead time variability and demand variability."
            else:
                return "Inventory management is a critical component of supply chain management that involves ordering, storing, and using a company's inventory. This includes the management of raw materials, components, and finished products, as well as warehousing and processing such items."
        
        elif "order" in query_lower:
            if "track" in query_lower:
                return "Order tracking allows customers and businesses to monitor the status of an order from placement to delivery. Our system provides real-time updates on order status, location, and estimated delivery time."
            elif "process" in query_lower:
                return "Order processing involves the steps required to complete a customer order, including order entry, picking, packing, shipping, and delivery. Efficient order processing is essential for customer satisfaction and operational efficiency."
            else:
                return "Order management is the process of tracking orders from inception to fulfillment. It includes order entry, processing, fulfillment, and after-sales service. An effective order management system ensures that orders are fulfilled accurately and efficiently."
        
        elif "supply chain" in query_lower:
            return "Supply chain management (SCM) is the management of the flow of goods and services between businesses and locations. This includes the movement and storage of raw materials, work-in-process inventory, finished goods, and end-to-end order fulfillment from the point of origin to the point of consumption."
        
        # Default response
        return "Based on the available information, I can provide insights on various aspects of supply chain management, including inventory management, order processing, and logistics. Please specify your question for more detailed information."