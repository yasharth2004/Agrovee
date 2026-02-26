"""
RAG Chatbot Service
Retrieval-Augmented Generation for agricultural Q&A
Uses Ollama (phi model) for LLM generation + FAISS for retrieval
"""

import numpy as np
from typing import List, Dict, Optional
import logging
import json
import os
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi")

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
    Uses FAISS for retrieval and Ollama (phi) for generation
    """
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.knowledge_base = []
        self.knowledge_embeddings = None
        self.ollama_available = False
        self._load_knowledge_base()
        self._initialize_embeddings()
        self._check_ollama()
    
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

    def _check_ollama(self):
        """Check if Ollama is available and the model is loaded"""
        try:
            resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
                model_name = OLLAMA_MODEL.split(":")[0]
                if model_name in models:
                    self.ollama_available = True
                    logger.info(f"✓ Ollama connected — using model '{OLLAMA_MODEL}'")
                else:
                    logger.warning(f"Ollama running but model '{OLLAMA_MODEL}' not found. Available: {models}")
            else:
                logger.warning("Ollama API responded with non-200 status")
        except Exception as e:
            logger.warning(f"Ollama not reachable at {OLLAMA_BASE_URL}: {e}")
            self.ollama_available = False
    
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
        Generate response using Ollama LLM with RAG context.
        Falls back to template-based if Ollama is unavailable.
        """
        # Build context string from retrieved docs (no source markers — model parrots them)
        context_text = ""
        for doc in retrieved_docs:
            context_text += f"Q: {doc['question']}\nA: {doc['answer']}\n\n"

        # Add user context if available
        extra_context = ""
        if context:
            if "crop" in context and context["crop"]:
                extra_context += f"The user is growing {context['crop']}. "
            if "disease" in context and context["disease"]:
                extra_context += f"The user's crop has been diagnosed with {context['disease']}. "
            if "confidence" in context and context["confidence"]:
                extra_context += f"Diagnosis confidence: {context['confidence']:.1f}%. "
            if "risk" in context and context["risk"]:
                extra_context += f"Risk level: {context['risk']}. "
            if "weather" in context and context["weather"]:
                extra_context += f"Current weather: {context['weather']}. "
            if "treatments" in context and context["treatments"]:
                extra_context += f"Recommended treatments: {context['treatments']}. "
            if "prevention" in context and context["prevention"]:
                extra_context += f"Prevention tips: {context['prevention']}. "

        # Try Ollama first
        if self.ollama_available:
            try:
                return self._call_ollama(user_message, context_text, extra_context)
            except Exception as e:
                logger.error(f"Ollama generation failed, falling back to template: {e}")

        # Template-based fallback
        return self._template_response(user_message, retrieved_docs, context)

    def _call_ollama(self, user_message: str, context_text: str, extra_context: str) -> str:
        """Call Ollama API to generate a response"""
        system_prompt = (
            "You are Agrovee AI, a senior agronomist and plant pathologist with 20 years of field experience. "
            "You work inside the Agrovee crop-health platform. You speak like a knowledgeable farming expert "
            "who has personally dealt with every common crop disease.\n\n"
            "YOUR VOICE:\n"
            "- Confident and direct. You KNOW the answer — never hedge with 'I suggest you consult someone else'.\n"
            "- Practical: give exact steps a farmer can do TODAY.\n"
            "- Use bullet points for treatment steps.\n"
            "- Keep answers 80-120 words. Be dense with useful info, no filler.\n\n"
            "STRICT RULES:\n"
            "1. NEVER say 'As an AI', 'As an Agrovee assistant', 'As a language model', or similar. You are a farming expert, period.\n"
            "2. NEVER mention sources, references, citations, or '[Source]'. Just state facts directly.\n"
            "3. NEVER say 'consult your local agronomist' or 'consult an expert' — YOU are the expert.\n"
            "4. NEVER generate fake conversations, follow-up questions you answer yourself, puzzles, or scenarios.\n"
            "5. Give ONE direct answer, then STOP.\n"
            "6. Use emoji sparingly: 🌱 🌾 💧 🐛 ✅\n"
        )

        user_prompt = f"""Agricultural knowledge:
{context_text}
{extra_context}
Farmer asks: {user_message}

Answer as a confident farming expert. Be specific and actionable. No source references. One answer, then stop."""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "top_p": 0.8,
                "num_predict": 200,
                "repeat_penalty": 1.3,
                "stop": ["\nUser:", "\nuser:", "\nAssistant:", "\nassistant:", "\nFarmer:", "\nfarmer:", "\nImagine", "\nQuestion:", "\nConsider", "\nHint:", "\nExercise", "\nNote:", "\nScenario", "\nPuzzle", "```", "\n\n\n"],
            }
        }

        logger.info(f"Sending request to Ollama ({OLLAMA_MODEL})...")
        resp = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120.0  # phi can take a moment on CPU
        )
        resp.raise_for_status()
        result = resp.json()
        answer = result.get("response", "").strip()

        if not answer:
            raise ValueError("Ollama returned empty response")

        # Post-process: trim any off-topic rambling the model may append
        answer = self._clean_response(answer)

        logger.info(f"Ollama response received ({len(answer)} chars)")
        return answer

    @staticmethod
    def _clean_response(text: str) -> str:
        """Strip off-topic content that phi sometimes appends."""
        import re

        # Remove [Source N] / [source N] references the model may parrot
        text = re.sub(r'\[(?:[Ss]ource\s*\d+)\]', '', text)
        # Remove "from reputable sources" type filler
        text = re.sub(r',?\s*(?:from|based on)\s+(?:reputable|reliable|trusted)\s+sources?[^.]*\.?', '.', text, flags=re.IGNORECASE)
        # Remove "As an Agrovee assistant/AI" openings
        text = re.sub(r'^(?:Hi!?\s*)?As an? Agrovee (?:assistant|AI)[,.]?\s*', '', text, flags=re.IGNORECASE)
        # Remove "consult your local agronomist" type hedging
        text = re.sub(r'I (?:suggest|recommend|advise) (?:you )?(?:to )?consult (?:your )?(?:local )?(?:agronomist|expert|specialist)[^.]*\.?\s*', '', text, flags=re.IGNORECASE)

        # Cut at any fake continuation pattern
        cut_markers = [
            "\nUser:", "\nuser:", "\nAssistant:", "\nassistant:",
            "\nFarmer:", "\nfarmer:", "\nHuman:", "\nhuman:",
            "\nImagine ", "\nQuestion:", "\nConsider a",
            "\nYou are a ", "\nNote:", "\nExercise",
            "\nHint:", "\nFirst, identify", "\nScenario",
            "\nAs an AI", "\nAs an Agrovee", "\nHowever, due to",
            "\nLet me ", "\nNow, ", "\nIn this scenario",
            "\nAgrovee AI has", "\nPuzzle", "```",
            "\n1. The farmer",
        ]
        for marker in cut_markers:
            idx = text.find(marker)
            if idx > 30:
                text = text[:idx].rstrip()

        # Line-level filtering
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("user:") or stripped.startswith("assistant:") or stripped.startswith("farmer:"):
                break
            if "user input from" in stripped or "farmer's question from" in stripped:
                break
            if "from agrovee's knowledge base" in stripped or "from his/her dashboard" in stripped:
                break
            clean_lines.append(line)

        # Clean up double spaces / double periods from removals
        result = "\n".join(clean_lines).strip()
        result = re.sub(r'\s{2,}', ' ', result)
        result = re.sub(r'\.{2,}', '.', result)
        result = re.sub(r'\s*,\s*,', ',', result)
        result = re.sub(r',\s*\.', '.', result)
        return result.strip()

    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate response when no relevant documents found — try Ollama first"""
        if self.ollama_available:
            try:
                return self._call_ollama(
                    user_message,
                    context_text="No specific documents matched in the Agrovee knowledge base for this query. Use your general agricultural expertise to help.",
                    extra_context=""
                )
            except Exception as e:
                logger.error(f"Ollama fallback failed: {e}")

        return self._static_fallback_response()

    def _template_response(self, user_message: str, retrieved_docs: List[Dict], context: Optional[Dict]) -> str:
        """Template-based response (used when Ollama is unavailable)"""
        if retrieved_docs and retrieved_docs[0]["score"] > 0.7:
            top_doc = retrieved_docs[0]
            response = f"🌱 Great question! Here's what I know:\n\n{top_doc['answer']}\n"

            if context:
                if "crop" in context:
                    response += f"\n💡 Since you're growing **{context['crop']}**, this is especially relevant."
                if "disease" in context:
                    response += f"\n🔍 This ties into your recent diagnosis of **{context['disease']}** — check the Dashboard for updated risk scores."

            if len(retrieved_docs) > 1:
                response += "\n\n📚 **You might also want to know:**\n"
                for doc in retrieved_docs[1:]:
                    response += f"• {doc['question']}\n"

            response += "\nAnything else I can help with? 🌾"
            return response

        response = "🌱 Here's what Agrovee recommends based on best practices:\n\n"
        for doc in retrieved_docs[:2]:
            response += f"{doc['answer']}\n\n"
        response += "💡 **Tip:** Upload a leaf photo on the **Diagnose** page for a more precise AI analysis!\n"
        response += "\nFeel free to ask me anything else! 🌾"
        return response

    def _static_fallback_response(self) -> str:
        """Static fallback when no LLM and no retrieval results"""
        return """👋 Hey there! I'm Agrovee AI — your smart farming companion.

I don't have a specific answer for that in my knowledge base yet, but here's what I'd suggest:

🌿 **For plant health issues:**
• Upload a leaf photo on the **Diagnose** page — I can identify 38 crop diseases from images!
• Check your **Dashboard** for weather-adjusted disease risk scores.

💧 **General crop tips:**
• Ensure proper spacing and air circulation
• Monitor soil moisture — overwatering is the #1 mistake
• Keep an eye on pests early — prevention beats treatment

🌤️ **Weather matters:**
• Your Dashboard shows real-time weather data for your area
• High humidity + warm temps = higher disease risk

Try asking me something specific like:
• "How do I treat powdery mildew?"
• "What fertilizer should I use for tomatoes?"
• "Signs of overwatering?"

I'm here to help! 🌾"""


# Global instance
_chatbot_service = None

def get_chatbot_service() -> RAGChatbotService:
    """Get or create chatbot service singleton"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = RAGChatbotService()
    return _chatbot_service
