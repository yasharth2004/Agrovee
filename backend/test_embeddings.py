#!/usr/bin/env python
"""Test script to verify embeddings and RAG are working"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.services.rag_chatbot import RAGChatbotService, DISABLE_TORCH, EMBEDDINGS_AVAILABLE

print("=" * 60)
print("Agrovee RAG Chatbot - Debug Test")
print("=" * 60)
print()

# Check configuration
print(f"AGROVEE_DISABLE_TORCH: {settings.AGROVEE_DISABLE_TORCH}")
print(f"DISABLE_TORCH (computed): {DISABLE_TORCH}")
print(f"EMBEDDINGS_AVAILABLE: {EMBEDDINGS_AVAILABLE}")
print()

# Initialize chatbot
print("Initializing RAG Chatbot Service...")
chatbot = RAGChatbotService()
print()

# Test queries
test_queries = [
    "How to prevent fungal diseases in rice?",
    "What causes yellow leaves in plants?",
    "How to manage aphids?",
    "Best time for fertilizer application?",
]

print("Testing RAG Retrieval:")
print("-" * 60)
for query in test_queries:
    print(f"\n📝 Query: {query}")
    
    # Get response
    response = chatbot.chat(query)
    
    # Show retrieved documents
    if response["retrieved_docs"]:
        print("📌 Retrieved Documents:")
        for i, doc in enumerate(response["retrieved_docs"], 1):
            print(f"  {i}. {doc['question']}")
            print(f"     Score: {doc['score']:.3f}")
            print(f"     ID: {doc['id']}")
    else:
        print("  ❌ No documents retrieved (EMBEDDINGS NOT WORKING!)")
    
    print()
    print(f"💬 Answer: {response['answer'][:150]}...")
    print()

print("=" * 60)
print("✅ Test Complete!")
print("=" * 60)
