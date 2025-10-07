#!/usr/bin/env python3
"""
Test script to upload a sample document to Pinecone and verify embeddings
"""

import os
from dotenv import load_dotenv
from rag.rag_handler import RAGHandler

# Load environment variables
load_dotenv()

def test_document_upload():
    """Test uploading a document to Pinecone"""
    
    print("🧪 Testing Document Upload to Pinecone...")
    print("=" * 50)
    
    # Initialize RAG handler
    try:
        rag_handler = RAGHandler(mock=False, api_key=os.environ.get("PINECONE_API_KEY"))
        print("✅ RAG Handler initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG Handler: {e}")
        return
    
    # Test document
    test_doc = {
        "text": "Supply chain resilience refers to the ability of a supply chain to prepare for unexpected risk events, respond and recover quickly to potential disruptions to return to its original situation or grow by moving to a new, more desirable state in order to increase customer service, market share and financial performance.",
        "metadata": {
            "file_name": "test_document.txt",
            "chunk_index": 0,
            "topic": "supply chain resilience"
        }
    }
    
    # Upload the document
    try:
        print("\n📤 Uploading test document...")
        doc_id = rag_handler.add_document(
            text=test_doc["text"],
            metadata=test_doc["metadata"]
        )
        print(f"✅ Document uploaded with ID: {doc_id}")
    except Exception as e:
        print(f"❌ Failed to upload document: {e}")
        return
    
    # Test search
    try:
        print("\n🔍 Testing search functionality...")
        results = rag_handler.search("supply chain resilience", top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n   Result {i}:")
                print(f"   - ID: {result.get('id', 'N/A')}")
                print(f"   - Score: {result.get('score', 'N/A'):.4f}")
                
                # Handle metadata
                metadata = result.get('metadata', {})
                if isinstance(metadata, dict):
                    if 'text' in metadata:
                        text_preview = metadata['text'][:100] + "..." if len(metadata['text']) > 100 else metadata['text']
                        print(f"   - Text: {text_preview}")
                    if 'file_name' in metadata:
                        print(f"   - File: {metadata['file_name']}")
                    if 'topic' in metadata:
                        print(f"   - Topic: {metadata['topic']}")
        else:
            print("❌ No search results found")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_document_upload()