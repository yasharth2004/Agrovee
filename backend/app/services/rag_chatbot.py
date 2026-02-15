"""
RAG Chatbot Service
Retrieval-Augmented Generation for agricultural Q&A
"""

import numpy as np
from typing import List, Dict, Optional
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import AI dependencies
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available - running in demo mode")


class RAGChatbotService:
    """
    RAG-based chatbot for agricultural queries
    Uses FAISS for retrieval and HuggingFace for generation
    """
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.knowledge_base = []
        self.knowledge_embeddings = None
        self._load_knowledge_base()
        self._initialize_embeddings()
    
    def _load_knowledge_base(self):
        """Load agricultural knowledge base"""
        # In production, this would load from a file or database
        self.knowledge_base = [
            {
                "id": "kb_001",
                "question": "How to prevent early blight in tomatoes?",
                "answer": "Early blight can be prevented by: 1) Practicing crop rotation, 2) Removing infected plant debris, 3) Using disease-resistant varieties, 4) Applying mulch to prevent soil splash, 5) Avoiding overhead watering, 6) Ensuring good air circulation, 7) Applying preventive fungicides during humid weather.",
                "category": "disease_prevention",
                "crops": ["tomato"]
            },
            {
                "id": "kb_002",
                "question": "What causes yellow leaves in plants?",
                "answer": "Yellow leaves (chlorosis) can be caused by: 1) Nitrogen deficiency - apply nitrogen-rich fertilizer, 2) Overwatering - reduce watering and improve drainage, 3) Iron deficiency - apply chelated iron, especially in alkaline soils, 4) Natural aging - remove old leaves, 5) Pest infestation - inspect for aphids or mites, 6) Root problems - check for root rot.",
                "category": "diagnosis",
                "crops": ["general"]
            },
            {
                "id": "kb_003",
                "question": "When is the best time to apply fertilizer?",
                "answer": "Best timing for fertilizer application: 1) Base application: At planting time, mix into soil, 2) Top dressing: During active growth phase (every 2-4 weeks), 3) Morning application: Early morning is ideal for liquid fertilizers, 4) Pre-rain application: For granular fertilizers, apply before expected rain, 5) Avoid: During extreme heat or drought stress, 6) Foliar feeding: During cool mornings or evenings.",
                "category": "fertilizer",
                "crops": ["general"]
            },
            {
                "id": "kb_004",
                "question": "How to manage powdery mildew organically?",
                "answer": "Organic management of powdery mildew: 1) Milk spray: Mix 40% milk with 60% water, spray weekly, 2) Baking soda spray: 1 tbsp baking soda + 1 tsp dish soap per gallon water, 3) Neem oil: Apply according to label, 4) Sulfur dust: Apply as preventive, 5) Improve air circulation: Prune and space plants properly, 6) Remove infected parts: Dispose away from garden, 7) Plant resistant varieties.",
                "category": "organic_treatment",
                "crops": ["general"]
            },
            {
                "id": "kb_005",
                "question": "What is NPK ratio and how to choose it?",
                "answer": "NPK ratio explained: N (Nitrogen) for leaf growth, P (Phosphorus) for roots and flowers, K (Potassium) for overall plant health. Choose based on plant stage: 1) Seedlings: 10-10-10 (balanced), 2) Leafy vegetables: 20-10-10 (high N), 3) Flowering/fruiting: 5-10-10 (low N, high P), 4) Root vegetables: 5-10-10 (high P and K), 5) General maintenance: 10-10-10. Soil test helps determine specific needs.",
                "category": "fertilizer",
                "crops": ["general"]
            },
            {
                "id": "kb_006",
                "question": "Signs of overwatering vs underwatering?",
                "answer": "Overwatering signs: 1) Yellow leaves (lower leaves first), 2) Soft, wilted leaves, 3) Root rot smell, 4) Mold on soil, 5) Slow growth. Underwatering signs: 1) Dry, crispy leaves, 2) Wilting (firm leaves), 3) Slow growth, 4) Leaf drop, 5) Soil pulling away from pot edges. Solution: Overwatered - improve drainage, reduce watering, let soil dry. Underwatered - water deeply, add mulch.",
                "category": "irrigation",
                "crops": ["general"]
            },
            {
                "id": "kb_007",
                "question": "How to manage aphid infestation?",
                "answer": "Aphid control methods: 1) Water spray: Strong spray to dislodge aphids, 2) Neem oil: Apply weekly, 3) Insecticidal soap: Spray on contact, 4) Beneficial insects: Introduce ladybugs, lacewings, 5) Sticky traps: Yellow traps for monitoring, 6) Reflective mulch: Repels aphids, 7) Companion planting: Grow garlic, chives near susceptible plants, 8) Remove heavily infested parts.",
                "category": "pest_management",
                "crops": ["general"]
            },
            {
                "id": "kb_008",
                "question": "Crop rotation benefits and how to implement?",
                "answer": "Crop rotation benefits: 1) Breaks disease cycles, 2) Reduces pest buildup, 3) Improves soil health, 4) Balances nutrient use. Implementation: 1) Divide garden into plots, 2) Group crops by family (nightshades, legumes, brassicas, etc.), 3) Rotate families yearly: Year 1 - tomatoes in plot A, Year 2 - beans in plot A, Year 3 - cabbage in plot A, 4) Avoid planting same family in same plot for 3-4 years, 5) Follow heavy feeders with nitrogen fixers (legumes).",
                "category": "prevention",
                "crops": ["general"]
            }
        ]
        
        logger.info(f"Loaded {len(self.knowledge_base)} knowledge base entries")
    
    def _initialize_embeddings(self):
        """Initialize embedding model and FAISS index"""
        if not EMBEDDINGS_AVAILABLE:
            logger.warning("Running in demo mode - semantic search unavailable")
            return
        
        try:
            # Load embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✓ Embedding model loaded")
            
            # Create embeddings for knowledge base
            texts = [f"{item['question']} {item['answer']}" for item in self.knowledge_base]
            self.knowledge_embeddings = self.embedding_model.encode(texts)
            
            # Create FAISS index
            dimension = self.knowledge_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.knowledge_embeddings.astype('float32'))
            
            logger.info(f"✓ FAISS index created with {len(self.knowledge_base)} documents")
            
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            self.embedding_model = None
            self.index = None
    
    def chat(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """
        Process user message and generate response
        
        Args:
            user_message: User's question
            context: Optional context (user history, current diagnosis, etc.)
            
        Returns:
            Response with answer, sources, and confidence
        """
        try:
            # Retrieve relevant documents
            retrieved_docs = self._retrieve(user_message, top_k=3)
            
            # Generate response
            if retrieved_docs:
                answer = self._generate_response(user_message, retrieved_docs, context)
            else:
                answer = self._generate_fallback_response(user_message)
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "id": doc["id"],
                        "title": doc["question"],
                        "relevance_score": doc["score"]
                    }
                    for doc in retrieved_docs
                ],
                "retrieved_docs": retrieved_docs,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your question. Please try rephrasing or contact support.",
                "sources": [],
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant documents from knowledge base"""
        if not EMBEDDINGS_AVAILABLE or self.index is None:
            # Fallback to keyword matching
            return self._keyword_search(query, top_k)
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query])
            
            # Search FAISS index
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Get documents with scores
            retrieved = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.knowledge_base):
                    doc = self.knowledge_base[idx].copy()
                    doc["score"] = float(1 / (1 + distance))  # Convert distance to similarity
                    retrieved.append(doc)
            
            return retrieved
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        keywords = query_lower.split()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.knowledge_base:
            text = f"{doc['question']} {doc['answer']}".lower()
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                doc_copy = doc.copy()
                doc_copy["score"] = score / len(keywords)
                scored_docs.append(doc_copy)
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]
    
    def _generate_response(self, user_message: str, retrieved_docs: List[Dict], context: Optional[Dict]) -> str:
        """
        Generate response based on retrieved documents
        
        In production, this would use an LLM (GPT, LLaMA, etc.)
        For now, we use a template-based approach
        """
        # Check if query is directly answered by top document
        if retrieved_docs and retrieved_docs[0]["score"] > 0.7:
            top_doc = retrieved_docs[0]
            
            # Format response
            response = f"{top_doc['answer']}\n\n"
            
            # Add context-specific information
            if context:
                if "crop" in context:
                    response += f"\n💡 This advice is particularly relevant for {context['crop']}."
                if "disease" in context:
                    response += f"\n🔍 Related to your diagnosis: {context['disease']}"
            
            # Add related information from other docs
            if len(retrieved_docs) > 1:
                response += "\n\n**Related information:**\n"
                for doc in retrieved_docs[1:]:
                    response += f"• {doc['question']}\n"
            
            return response
        
        # Synthesize from multiple sources
        response = "Based on agricultural best practices:\n\n"
        
        for i, doc in enumerate(retrieved_docs[:2], 1):
            response += f"{doc['answer']}\n\n"
        
        response += "\n💬 For specific conditions on your farm, consider consulting a local agricultural expert."
        
        return response
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate fallback response when no relevant documents found"""
        return """I don't have specific information about that in my knowledge base. However, here are some general guidelines:
        
1. For disease issues: Ensure proper plant spacing, good air circulation, and avoid overhead watering
2. For growth problems: Check soil pH, ensure adequate nutrition, and maintain consistent watering
3. For pest issues: Monitor regularly, use integrated pest management (IPM) practices

For specific guidance, I recommend:
- Consulting your local agricultural extension office
- Sharing photos of the issue for better diagnosis
- Getting soil testing done

Is there something more specific I can help you with?"""


# Global instance
_chatbot_service = None

def get_chatbot_service() -> RAGChatbotService:
    """Get or create chatbot service singleton"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = RAGChatbotService()
    return _chatbot_service
