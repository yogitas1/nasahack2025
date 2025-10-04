#!/usr/bin/env python3
"""
Test script for the RAG search system.
"""

import os
from dotenv import load_dotenv
from rag_search import search_knowledge, generate_answer

# Load environment variables
load_dotenv()

def test_search_only():
    """Test just the search functionality."""
    print("=== Testing Search Functionality ===")
    
    query = "What infrastructure projects are happening in Kenya?"
    print(f"Query: {query}")
    
    try:
        relevant_chunks = search_knowledge(query, top_k=3)
        print(f"\nFound {len(relevant_chunks)} relevant chunks:")
        
        for i, chunk in enumerate(relevant_chunks, 1):
            print(f"\n--- Chunk {i} ---")
            print(f"Source: {chunk['source']}")
            print(f"Text: {chunk['text'][:200]}...")
            
    except Exception as e:
        print(f"Error in search: {e}")

def test_full_rag():
    """Test the complete RAG pipeline."""
    print("\n=== Testing Full RAG Pipeline ===")
    
    query = "What are the main challenges facing African infrastructure development?"
    print(f"Query: {query}")
    
    try:
        # Get relevant chunks
        relevant_chunks = search_knowledge(query, top_k=5)
        print(f"\nRetrieved {len(relevant_chunks)} relevant chunks")
        
        # Generate answer
        answer = generate_answer(query, relevant_chunks)
        print(f"\nGenerated Answer:\n{answer}")
        
    except Exception as e:
        print(f"Error in full RAG: {e}")

def interactive_test():
    """Interactive testing mode."""
    print("\n=== Interactive RAG Testing ===")
    print("Enter your questions about African infrastructure (type 'quit' to exit)")
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        if not query:
            continue
            
        try:
            relevant_chunks = search_knowledge(query, top_k=3)
            answer = generate_answer(query, relevant_chunks)
            print(f"\nAnswer: {answer}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables!")
        print("Please set your API key in the .env file")
        exit(1)
    
    print("🚀 Testing RAG Search System")
    
    # Run tests
    test_search_only()
    test_full_rag()
    
    # Ask if user wants interactive mode
    response = input("\nWould you like to try interactive mode? (y/n): ")
    if response.lower().startswith('y'):
        interactive_test()
    
    print("\n✅ Testing complete!")
