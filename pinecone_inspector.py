#!/usr/bin/env python3
"""
Pinecone Database Inspector
A comprehensive tool to check document embeddings in your Pinecone database
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

class PineconeInspector:
    def __init__(self):
        """Initialize the Pinecone Inspector"""
        self.api_key = os.environ.get("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ PINECONE_API_KEY not found in environment variables")
        
        self.pc = Pinecone(api_key=self.api_key)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def list_all_indexes(self):
        """List all available Pinecone indexes"""
        print("📋 Available Pinecone Indexes:")
        print("-" * 30)
        
        try:
            indexes = self.pc.list_indexes()
            index_names = indexes.names()
            
            if not index_names:
                print("   No indexes found")
                return []
            
            for i, name in enumerate(index_names, 1):
                print(f"   {i}. {name}")
            
            return index_names
        except Exception as e:
            print(f"❌ Error listing indexes: {e}")
            return []
    
    def get_index_stats(self, index_name):
        """Get detailed statistics for a specific index"""
        print(f"\n📊 Index Statistics for '{index_name}':")
        print("-" * 40)
        
        try:
            index = self.pc.Index(index_name)
            stats = index.describe_index_stats()
            
            print(f"   • Total vectors: {stats.total_vector_count:,}")
            print(f"   • Dimension: {stats.dimension}")
            print(f"   • Index fullness: {stats.index_fullness:.2%}")
            
            # Show namespace information if available
            if hasattr(stats, 'namespaces') and stats.namespaces:
                print(f"   • Namespaces: {list(stats.namespaces.keys())}")
            
            return stats
        except Exception as e:
            print(f"❌ Error getting index stats: {e}")
            return None
    
    def sample_documents(self, index_name, limit=5):
        """Retrieve sample documents from the index"""
        print(f"\n📄 Sample Documents from '{index_name}' (limit: {limit}):")
        print("-" * 50)
        
        try:
            index = self.pc.Index(index_name)
            stats = index.describe_index_stats()
            
            if stats.total_vector_count == 0:
                print("   📭 No documents found in the index")
                return []
            
            # Query with a dummy vector to get some results
            dummy_vector = [0.0] * stats.dimension
            results = index.query(
                vector=dummy_vector,
                top_k=min(limit, stats.total_vector_count),
                include_metadata=True
            )
            
            documents = []
            for i, match in enumerate(results.matches, 1):
                print(f"\n   📄 Document {i}:")
                print(f"      ID: {match.id}")
                print(f"      Score: {match.score:.4f}")
                
                if hasattr(match, 'metadata') and match.metadata:
                    metadata = match.metadata
                    print(f"      Metadata:")
                    
                    for key, value in metadata.items():
                        if key == 'text':
                            # Show first 150 characters of text
                            text_preview = str(value)[:150] + "..." if len(str(value)) > 150 else str(value)
                            print(f"         • {key}: {text_preview}")
                        else:
                            print(f"         • {key}: {value}")
                    
                    documents.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': metadata
                    })
                else:
                    print(f"      No metadata available")
                    documents.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': {}
                    })
            
            return documents
            
        except Exception as e:
            print(f"❌ Error sampling documents: {e}")
            return []
    
    def search_documents(self, index_name, query, top_k=5):
        """Search for documents using semantic similarity"""
        print(f"\n🔍 Search Results for '{query}' in '{index_name}':")
        print("-" * 60)
        
        try:
            index = self.pc.Index(index_name)
            
            # Create query vector
            query_vector = self.model.encode(query).tolist()
            
            # Perform search
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            
            if not results.matches:
                print("   📭 No matching documents found")
                return []
            
            search_results = []
            for i, match in enumerate(results.matches, 1):
                print(f"\n   🎯 Result {i}:")
                print(f"      ID: {match.id}")
                print(f"      Similarity Score: {match.score:.4f}")
                
                if hasattr(match, 'metadata') and match.metadata:
                    metadata = match.metadata
                    
                    if 'text' in metadata:
                        text_preview = str(metadata['text'])[:200] + "..." if len(str(metadata['text'])) > 200 else str(metadata['text'])
                        print(f"      Text: {text_preview}")
                    
                    if 'file_name' in metadata:
                        print(f"      File: {metadata['file_name']}")
                    
                    if 'chunk_index' in metadata:
                        print(f"      Chunk: {metadata['chunk_index']}")
                    
                    if 'topic' in metadata:
                        print(f"      Topic: {metadata['topic']}")
                    
                    search_results.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': metadata
                    })
            
            return search_results
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def inspect_specific_document(self, index_name, doc_id):
        """Retrieve and inspect a specific document by ID"""
        print(f"\n🔍 Inspecting Document '{doc_id}' in '{index_name}':")
        print("-" * 50)
        
        try:
            index = self.pc.Index(index_name)
            
            # Fetch the specific document
            result = index.fetch(ids=[doc_id])
            
            if doc_id not in result.vectors:
                print(f"   ❌ Document '{doc_id}' not found")
                return None
            
            vector_data = result.vectors[doc_id]
            
            print(f"   📄 Document Details:")
            print(f"      ID: {doc_id}")
            print(f"      Vector Dimension: {len(vector_data.values)}")
            
            if hasattr(vector_data, 'metadata') and vector_data.metadata:
                print(f"      Metadata:")
                for key, value in vector_data.metadata.items():
                    if key == 'text':
                        print(f"         • {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
                    else:
                        print(f"         • {key}: {value}")
            
            return vector_data
            
        except Exception as e:
            print(f"❌ Error inspecting document: {e}")
            return None
    
    def full_inspection(self, index_name="scm-documents"):
        """Perform a comprehensive inspection of the Pinecone index"""
        print("🔍 COMPREHENSIVE PINECONE INSPECTION")
        print("=" * 60)
        
        # 1. List all indexes
        indexes = self.list_all_indexes()
        
        # 2. Check if target index exists
        if index_name not in indexes:
            print(f"\n❌ Target index '{index_name}' not found")
            if indexes:
                print(f"💡 Available indexes: {', '.join(indexes)}")
                index_name = indexes[0]
                print(f"🔄 Using '{index_name}' instead")
            else:
                print("❌ No indexes available")
                return
        
        # 3. Get index statistics
        stats = self.get_index_stats(index_name)
        
        # 4. Sample documents
        if stats and stats.total_vector_count > 0:
            documents = self.sample_documents(index_name, limit=3)
            
            # 5. Perform sample searches
            search_queries = [
                "supply chain management",
                "inventory control",
                "logistics optimization"
            ]
            
            for query in search_queries:
                self.search_documents(index_name, query, top_k=2)
        
        print("\n" + "=" * 60)
        print("✅ Comprehensive inspection complete!")

def main():
    """Main function to run the Pinecone inspector"""
    try:
        inspector = PineconeInspector()
        
        # Run full inspection
        inspector.full_inspection()
        
        # Interactive mode
        print("\n" + "=" * 60)
        print("🎯 INTERACTIVE MODE")
        print("Available commands:")
        print("  1. search <query> - Search for documents")
        print("  2. inspect <doc_id> - Inspect specific document")
        print("  3. stats <index_name> - Get index statistics")
        print("  4. quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command.startswith("search "):
                    query = command[7:]
                    inspector.search_documents("scm-documents", query)
                elif command.startswith("inspect "):
                    doc_id = command[8:]
                    inspector.inspect_specific_document("scm-documents", doc_id)
                elif command.startswith("stats "):
                    index_name = command[6:]
                    inspector.get_index_stats(index_name)
                elif command == "help":
                    print("Available commands:")
                    print("  search <query> - Search for documents")
                    print("  inspect <doc_id> - Inspect specific document")
                    print("  stats <index_name> - Get index statistics")
                    print("  quit - Exit")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Failed to initialize Pinecone Inspector: {e}")

if __name__ == "__main__":
    main()