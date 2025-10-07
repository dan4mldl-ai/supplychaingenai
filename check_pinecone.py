#!/usr/bin/env python3
"""
Utility script to check document embeddings in Pinecone DB
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
import json

# Load environment variables
load_dotenv()

def check_pinecone_index():
    """Check the contents of the Pinecone index"""
    
    # Get API key from environment
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment variables")
        return
    
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # List all indexes
        indexes = pc.list_indexes()
        print(f"📋 Available indexes: {indexes.names()}")
        
        # Check our specific index
        index_name = "scm-documents"
        available_indexes = indexes.names()
        
        if index_name not in available_indexes:
            print(f"❌ Index '{index_name}' not found")
            
            # Check if there are other indexes we can examine
            if available_indexes:
                print(f"🔍 Let's check the existing index: {available_indexes[0]}")
                index_name = available_indexes[0]
            else:
                print("❌ No indexes found")
                return
        
        # Get index stats
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        
        print(f"\n📊 Index Statistics for '{index_name}':")
        print(f"   - Total vectors: {stats.total_vector_count}")
        print(f"   - Dimension: {stats.dimension}")
        print(f"   - Index fullness: {stats.index_fullness}")
        
        # Get some sample vectors (if any exist)
        if stats.total_vector_count > 0:
            print(f"\n🔍 Fetching sample vectors...")
            
            # Query with a dummy vector to get some results
            dummy_vector = [0.0] * stats.dimension
            results = index.query(
                vector=dummy_vector,
                top_k=min(10, stats.total_vector_count),
                include_metadata=True
            )
            
            print(f"\n📄 Sample Documents (showing up to 10):")
            for i, match in enumerate(results.matches, 1):
                print(f"\n   Document {i}:")
                print(f"   - ID: {match.id}")
                print(f"   - Score: {match.score:.4f}")
                
                if hasattr(match, 'metadata') and match.metadata:
                    metadata = match.metadata
                    print(f"   - Metadata:")
                    for key, value in metadata.items():
                        if key == 'text':
                            # Truncate long text for readability
                            text_preview = value[:100] + "..." if len(value) > 100 else value
                            print(f"     * {key}: {text_preview}")
                        else:
                            print(f"     * {key}: {value}")
                else:
                    print(f"   - No metadata available")
        else:
            print(f"\n📭 No vectors found in the index")
            
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {str(e)}")

def search_documents(query_text="supply chain"):
    """Search for documents with a specific query"""
    
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found")
        return
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Initialize model and Pinecone
        model = SentenceTransformer('all-MiniLM-L6-v2')
        pc = Pinecone(api_key=api_key)
        
        # Use existing index or the one we want
        indexes = pc.list_indexes().names()
        index_name = "scm-documents" if "scm-documents" in indexes else (indexes[0] if indexes else None)
        
        if not index_name:
            print("❌ No indexes available for search")
            return
            
        index = pc.Index(index_name)
        
        # Create query vector
        query_vector = model.encode(query_text).tolist()
        
        # Search
        results = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )
        
        print(f"\n🔍 Search Results for '{query_text}' in index '{index_name}':")
        if results.matches:
            for i, match in enumerate(results.matches, 1):
                print(f"\n   Result {i}:")
                print(f"   - ID: {match.id}")
                print(f"   - Similarity Score: {match.score:.4f}")
                
                if hasattr(match, 'metadata') and match.metadata:
                    metadata = match.metadata
                    if 'text' in metadata:
                        text_preview = metadata['text'][:200] + "..." if len(metadata['text']) > 200 else metadata['text']
                        print(f"   - Text: {text_preview}")
                    if 'file_name' in metadata:
                        print(f"   - File: {metadata['file_name']}")
                    if 'chunk_index' in metadata:
                        print(f"   - Chunk: {metadata['chunk_index']}")
        else:
            print("   No matching documents found")
                    
    except Exception as e:
        print(f"❌ Error searching documents: {str(e)}")

def create_scm_index():
    """Create the SCM documents index if it doesn't exist"""
    
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found")
        return
    
    try:
        from pinecone import ServerlessSpec
        
        pc = Pinecone(api_key=api_key)
        index_name = "scm-documents"
        
        if index_name not in pc.list_indexes().names():
            print(f"🔨 Creating index '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=384,  # for all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index '{index_name}' created successfully!")
            
            # Wait a moment for the index to be ready
            import time
            print("⏳ Waiting for index to be ready...")
            time.sleep(10)
        else:
            print(f"✅ Index '{index_name}' already exists")
            
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        print("💡 Tip: Make sure your Pinecone plan supports serverless indexes")

if __name__ == "__main__":
    print("🔍 Checking Pinecone Database...")
    print("=" * 50)
    
    # First, create the index if it doesn't exist
    print("\n1️⃣ Creating SCM index if needed...")
    create_scm_index()
    
    # Check the index contents
    print("\n2️⃣ Checking index contents...")
    check_pinecone_index()
    
    # Search for documents
    print("\n3️⃣ Searching for documents...")
    search_documents("supply chain management")
    
    print("\n" + "=" * 50)
    print("✅ Pinecone check complete!")