"""
RAG Chatbot Service
Retrieval-Augmented Generation for agricultural Q&A
Uses Google Gemini API for LLM generation + FAISS for retrieval
"""

from typing import List, Dict, Optional
import logging
import os
import re
from datetime import datetime

from app.services.gemini_service import get_gemini_service
from app.core.config import settings

logger = logging.getLogger(__name__)

STOPWORDS = {
    "a", "about", "after", "an", "and", "are", "as", "at", "be", "best",
    "by", "can", "do", "does", "for", "from", "give", "how", "i", "in",
    "is", "it", "me", "my", "of", "on", "or", "should", "small", "tell",
    "the", "this", "to", "use", "what", "when", "where", "which", "with",
}

AGRICULTURE_SYNONYMS = {
    "fungal": {"fungal", "fungus", "fungicide", "disease", "blight", "mildew", "blast"},
    "fungus": {"fungal", "fungus", "fungicide", "disease", "blight", "mildew", "blast"},
    "diseases": {"disease", "diseases", "blight", "mildew", "rot", "blast"},
    "disease": {"disease", "diseases", "blight", "mildew", "rot", "blast"},
    "pesticides": {"pesticide", "pesticides", "pest", "insect", "aphid", "neem", "soap"},
    "pesticide": {"pesticide", "pesticides", "pest", "insect", "aphid", "neem", "soap"},
    "organic": {"organic", "neem", "soap", "milk", "baking", "sulfur"},
    "rice": {"rice", "paddy", "blast", "sheath", "bacterial"},
    "weather": {"weather", "humidity", "rain", "temperature", "dew", "wind", "moisture"},
    "humid": {"weather", "humidity", "rain", "dew", "moisture", "fungal"},
    "humidity": {"weather", "humidity", "rain", "dew", "moisture", "fungal"},
    "strawberry": {"strawberry", "leaf", "scorch", "spot", "fungal"},
    "scorch": {"scorch", "leaf", "strawberry", "fungal", "spot"},
    "cause": {"cause", "caused", "causes", "reason", "source", "pathogen", "why"},
    "treat": {"treat", "treatment", "manage", "control", "spray", "fungicide", "remove"},
}

# Use a chat-specific flag for the heavy embedding stack. Do not reuse
# AGROVEE_DISABLE_TORCH here: the diagnosis model needs Torch enabled.
DISABLE_EMBEDDINGS = os.getenv("AGROVEE_DISABLE_RAG_EMBEDDINGS", "1") == "1"

# Try to import AI dependencies when not explicitly disabled
EMBEDDINGS_AVAILABLE = False
if not DISABLE_EMBEDDINGS:
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        EMBEDDINGS_AVAILABLE = True
    except Exception as e:
        EMBEDDINGS_AVAILABLE = False
        logger.warning(f"sentence-transformers not available - using keyword RAG: {e}")


class RAGChatbotService:
    """
    RAG-based chatbot for agricultural queries
    Uses FAISS for retrieval and Google Gemini API for generation
    """
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.knowledge_base = []
        self.knowledge_embeddings = None
        self.gemini_service = None
        self._load_knowledge_base()
        self._initialize_embeddings()
        self._initialize_gemini()
    
    def _load_knowledge_base(self):
        """Load agricultural knowledge base"""
        # In production, this would load from a file or database
        self.knowledge_base = [
            {
                "id": "kb_001",
                "question": "How to prevent early blight in tomatoes?",
                "answer": "Tomato leaf blight is commonly caused by fungal pathogens such as Alternaria solani, especially when infected plant debris, warm humid weather, soil splash, and wet leaves are present. It usually starts as brown spots with target-like rings on older leaves. Reduce it by: 1) Removing infected leaves and crop debris, 2) Avoiding overhead watering, 3) Mulching to stop soil splash, 4) Improving spacing and airflow, 5) Rotating tomatoes away from the same bed for 2-3 years, 6) Using resistant varieties, 7) Applying preventive fungicide during humid disease pressure.",
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
            },
            {
                "id": "kb_009",
                "question": "How to prevent fungal diseases in rice?",
                "answer": "Prevent rice fungal diseases such as blast and sheath blight by: 1) Using certified resistant seed, 2) Avoiding dense planting so the canopy dries faster, 3) Keeping nitrogen balanced and avoiding excess urea, 4) Maintaining proper field drainage and avoiding long stagnant water during disease pressure, 5) Removing infected straw and volunteer plants, 6) Monitoring during humid weather, 7) Applying recommended fungicide only when symptoms or local advisories indicate risk.",
                "category": "disease_prevention",
                "crops": ["rice", "paddy"]
            },
            {
                "id": "kb_010",
                "question": "Best organic pesticides for small farms",
                "answer": "Good organic pesticide options for small farms include: 1) Neem oil for aphids, whiteflies, mites, and soft-bodied insects, 2) Insecticidal soap for direct-contact control, 3) Bacillus thuringiensis (Bt) for caterpillars, 4) Beauveria bassiana for whiteflies and some beetles, 5) Sticky traps for monitoring, 6) Beneficial insects and companion planting. Spray in the evening, test on a few leaves first, and always follow label rates.",
                "category": "organic_treatment",
                "crops": ["general"]
            },
            {
                "id": "kb_011",
                "question": "How does weather affect crop diseases?",
                "answer": "Weather drives crop disease by controlling how long leaves stay wet, how fast pathogens multiply, and how easily spores spread. Warm humid nights, dew, cloudy weather, and repeated rain favor fungal diseases such as blight, mildew, rust, rice blast, and sheath blight. Splashing rain moves spores from soil and infected debris onto lower leaves. Wind can spread spores across a field, while waterlogged soil weakens roots and makes plants more vulnerable. Farmers should watch disease risk after 2-3 humid or rainy days, avoid overhead irrigation, improve spacing and airflow, remove infected residue, and apply preventive sprays before severe symptoms appear.",
                "category": "disease_prevention",
                "crops": ["general", "rice", "tomato"]
            },
            {
                "id": "kb_012",
                "question": "How to treat strawberry leaf scorch?",
                "answer": "Strawberry leaf scorch is usually managed by reducing infected leaf material and keeping the canopy dry. Remove badly spotted or scorched leaves and take them out of the field, not into compost. Avoid overhead irrigation; water at soil level in the morning so leaves dry quickly. Thin crowded plants and remove weeds to improve airflow. Add clean mulch to reduce soil splash. For active spread, use a labeled strawberry fungicide such as captan or myclobutanil where permitted, rotating modes of action to avoid resistance. After harvest, renovate the bed by mowing old leaves and removing debris. Keep potassium nutrition balanced because stressed plants scorch faster.",
                "category": "disease_treatment",
                "crops": ["strawberry"]
            },
            {
                "id": "kb_013",
                "question": "What causes strawberry leaf scorch?",
                "answer": "Strawberry leaf scorch is commonly caused by a fungal leaf-spot pathogen that survives on infected leaves and plant debris. It spreads when rain splash, overhead irrigation, or wet handling moves spores onto healthy leaves. The disease becomes worse when the strawberry canopy stays damp for long periods, plants are crowded, weeds block airflow, or old infected leaves remain in the bed. Stressed plants show heavier scorch, especially when nutrition is unbalanced, roots are weak, or weather alternates between humid nights and warm days. The dark purple spots on leaves expand and merge, making the leaf edges look burned or scorched.",
                "category": "disease_cause",
                "crops": ["strawberry"]
            },
            {
                "id": "kb_014",
                "question": "How to treat apple black rot?",
                "answer": "Apple black rot is managed through a combination of sanitation, pruning, and fungicide application. Remove all infected branches and fruit, cutting 12 inches below visible cankers and disinfecting tools between cuts. Prune to improve air circulation and allow leaves to dry quickly. Clean up fallen fruit and leaves in autumn. Apply fungicides like captan or mancozeb when conditions favor the disease (warm, humid weather after rain). Avoid overhead irrigation to keep foliage dry. Thin fruit to reduce stress on remaining tissue. Apply dormant oils in late winter to kill spores on bark. Use resistant apple varieties when possible.",
                "category": "disease_treatment",
                "crops": ["apple"]
            },
            {
                "id": "kb_015",
                "question": "What causes apple black rot disease?",
                "answer": "Apple black rot is caused by the fungus Botryosphaeria obtusa, which survives on infected cankers, fruit, and dead wood. The disease becomes severe when trees are stressed by poor nutrition, drought, winter injury, or sunscald. Warm, moist conditions favor spore spread, especially during bloom and wet periods after hail or pruning wounds. The fungus enters through wounds, sunscald cracks, and natural openings. Black, sunken lesions develop on fruit, stems, and branches. The fruit mummifies and remains on the tree as a source of spores for next season. High nitrogen fertilizer can promote excessive shoot growth that increases susceptibility.",
                "category": "disease_cause",
                "crops": ["apple"]
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

    def _initialize_gemini(self):
        """Initialize Gemini service for text generation"""
        try:
            self.gemini_service = get_gemini_service()
            if self.gemini_service.is_available():
                logger.info("✓ Gemini service initialized and ready")
            else:
                logger.warning(
                    "Gemini service not available. "
                    "Ensure GEMINI_API_KEY environment variable is set and "
                    "google-generativeai package is installed."
                )
        except Exception as e:
            logger.error(f"Error initializing Gemini service: {e}")
            self.gemini_service = None
    
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
            # Retrieve relevant documents. Diagnosis context is added to the
            # search query so follow-up questions stay grounded in the result.
            retrieval_query = self._build_retrieval_query(user_message, context)
            retrieved_docs = self._retrieve(retrieval_query, top_k=3, context=context)
            
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
    
    def _retrieve(self, query: str, top_k: int = 3, context: Optional[Dict] = None) -> List[Dict]:
        """Retrieve relevant documents from knowledge base
        
        Args:
            query: Search query
            top_k: Number of documents to return
            context: Optional context (crop, disease, etc.) for filtering
            
        Returns:
            List of relevant documents
        """
        if not EMBEDDINGS_AVAILABLE or self.index is None:
            # Fallback to keyword matching
            return self._keyword_search(query, top_k, context)
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query])
            
            # Search FAISS index
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k * 3)  # Get more candidates for filtering
            
            # Get documents with scores
            retrieved = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.knowledge_base):
                    doc = self.knowledge_base[idx].copy()
                    doc["score"] = float(1 / (1 + distance))  # Convert distance to similarity
                    retrieved.append(doc)
            
            # STRICT crop filtering if context provided
            if context and context.get("crop"):
                crop_name = context["crop"].lower()
                # Only keep docs that match the crop or are general
                matching_crop = [
                    d for d in retrieved 
                    if crop_name in " ".join(d.get("crops", [])).lower() 
                    or "general" in d.get("crops", [])
                ]
                # If we have matching docs for this crop, use only those
                if matching_crop:
                    retrieved = matching_crop
                else:
                    # Only return general docs if no crop-specific docs found
                    retrieved = [d for d in retrieved if "general" in d.get("crops", [])]
            
            return retrieved[:top_k]
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self._keyword_search(query, top_k, context)
    
    def _keyword_search(self, query: str, top_k: int = 3, context: Optional[Dict] = None) -> List[Dict]:
        """Fallback keyword-based search with strict crop filtering"""
        exact_terms = set(self._tokenize(query, expand=False))
        expanded_terms = set(self._tokenize(query)) - exact_terms
        intent = self._detect_intent(query)
        if not exact_terms and not expanded_terms:
            return []
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.knowledge_base:
            text = (
                f"{doc['question']} {doc['answer']} {doc['category']} "
                f"{' '.join(doc.get('crops', []))}"
            )
            doc_terms = set(self._tokenize(text, expand=False))
            question_terms = set(self._tokenize(doc["question"], expand=False))
            score = 0.0
            for term in exact_terms:
                if term in doc_terms:
                    score += 2.0
                if term in question_terms:
                    score += 1.5
                if term in doc.get("crops", []):
                    score += 1.0
                if term == doc.get("category"):
                    score += 0.5
            for term in expanded_terms:
                if term in doc_terms:
                    score += 0.35
            if intent == "cause" and doc.get("category") == "disease_cause":
                score += 4.0
            elif intent == "treatment" and doc.get("category") == "disease_treatment":
                score += 4.0
            elif intent == "prevention" and doc.get("category") == "disease_prevention":
                score += 2.0
            
            # STRICT crop filtering - only include docs for the requested crop or general docs
            if context and context.get("crop"):
                crop_name = context["crop"].lower()
                doc_crops_lower = [c.lower() for c in doc.get("crops", [])]
                crop_match = crop_name in doc_crops_lower or any(crop_name.startswith(c) or c.startswith(crop_name) for c in doc_crops_lower)
                general_doc = "general" in doc_crops_lower
                
                # Only score if it matches the crop or is a general doc
                if not (crop_match or general_doc):
                    continue  # Skip docs for other crops
                    
                # Boost score significantly for crop-specific matches
                if crop_match:
                    score += 5.0
            
            if score > 0:
                doc_copy = doc.copy()
                doc_copy["score"] = score / max(len(exact_terms) * 3.5, 1)
                scored_docs.append(doc_copy)
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

    def _build_retrieval_query(self, user_message: str, context: Optional[Dict]) -> str:
        """Combine the user question with diagnosis context for retrieval only."""
        if not context:
            return user_message

        context_parts = []
        for key in ("crop", "disease", "risk", "treatments", "prevention"):
            value = context.get(key)
            if value:
                context_parts.append(str(value))

        return " ".join([user_message, *context_parts]).strip()

    @staticmethod
    def _tokenize(text: str, expand: bool = True) -> List[str]:
        """Tokenize search text and keep agriculturally meaningful words."""
        raw_terms = re.findall(r"[a-z0-9]+", text.lower())
        terms = []
        for term in raw_terms:
            if len(term) <= 2 or term in STOPWORDS:
                continue
            if term in {"caused", "causes", "causing"}:
                term = "cause"
            elif term in {"treated", "treats", "treating", "treatment"}:
                term = "treat"
            elif term in {"managed", "manages", "managing", "management"}:
                term = "manage"
            elif term.endswith("ies") and len(term) > 4:
                term = f"{term[:-3]}y"
            elif term.endswith("es") and len(term) > 4:
                term = term[:-2]
            elif term.endswith("s") and len(term) > 3:
                term = term[:-1]
            terms.append(term)
            if expand:
                terms.extend(AGRICULTURE_SYNONYMS.get(term, set()))
        return terms

    @staticmethod
    def _detect_intent(query: str) -> str:
        """Detect the user's follow-up intent so diagnosis context doesn't flatten answers."""
        terms = set(RAGChatbotService._tokenize(query, expand=True))
        if terms & {"cause", "reason", "source", "pathogen", "why"}:
            return "cause"
        if terms & {"treat", "treatment", "manage", "control", "spray", "fungicide"}:
            return "treatment"
        if terms & {"prevent", "prevention", "avoid", "stop"}:
            return "prevention"
        return "general"
    
    def _generate_response(self, user_message: str, retrieved_docs: List[Dict], context: Optional[Dict]) -> str:
        """
        Generate response using Gemini LLM with RAG context.
        Falls back to template-based if Gemini is unavailable.
        """
        # Build context string from retrieved docs
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

        # Try Gemini first
        if self.gemini_service and self.gemini_service.is_available():
            try:
                answer = self._call_gemini(user_message, context_text, extra_context)
                if self._is_low_quality_answer(answer):
                    raise ValueError(f"Gemini returned too-short answer: {answer!r}")
                return answer
            except Exception as e:
                logger.error(f"Gemini generation failed, falling back to template: {e}")

        # Template-based fallback
        return self._template_response(user_message, retrieved_docs, context)

    def _call_gemini(self, user_message: str, context_text: str, extra_context: str) -> str:
        """Call Gemini API to generate a response"""
        system_prompt = (
            "You are Agrovee AI, a friendly and experienced farm advisor from Agrovee. "
            "You answer crop health questions like a helpful local agronomist—practical, warm, and farmer-focused.\n\n"
            "YOUR VOICE:\n"
            "- Farmer-friendly and easy to understand.\n"
            "- Explain the why briefly (1–2 sentences), then jump to what to do.\n"
            "- Use clear action steps (1, 2, 3) when recommending treatments or prevention.\n"
            "- Keep responses 100–160 words — short enough for a farmer to read quickly.\n"
            "- Use emojis sparingly for visual breaks: 🌱 🌾 💧 🐛 ✅\n\n"
            "CRITICAL RULE — DISEASE/CROP SPECIFICITY:\n"
            "⚠️ Answer ONLY about the specific crop and disease the farmer is asking about.\n"
            "- If the knowledge mentions a different crop or disease, ignore it.\n"
            "- Example: If crop is Apple with Black Rot, answer ONLY about Apple Black Rot. Do NOT mention Strawberry, Tomato, or any other disease.\n"
            "- Always verify your answer applies to the current crop and disease.\n\n"
            "RULES:\n"
            "1. NO phrases like 'As an AI', 'I'm a language model', or 'consult an expert' — you ARE the expert.\n"
            "2. NO source citations or '[Source]' references.\n"
            "3. Complete sentences — no fragments or bullet points unless listing steps.\n"
            "4. NO fake conversations or follow-up questions you answer yourself.\n"
        )

        user_prompt = f"""Knowledge:
{context_text}
{extra_context}
Farmer asks: {user_message}

Answer directly with practical advice—keep it under 160 words. Only use knowledge that applies to this specific crop and disease. Do not mention other crops or diseases."""

        logger.info("Sending request to Gemini API...")
        response_text = self.gemini_service.generate_content(
            prompt=user_prompt,
            system_instruction=system_prompt,
            temperature=0.5,
            top_p=0.8,
            max_output_tokens=300,
            timeout=60,
            max_retries=3
        )

        if not response_text:
            raise ValueError("Gemini returned empty response")

        # Post-process: trim any off-topic rambling
        answer = self._clean_response(response_text)

        logger.info(f"Gemini response received ({len(answer)} chars)")
        return answer

    @staticmethod
    def _is_low_quality_answer(answer: str) -> bool:
        """Detect tiny or obviously incomplete LLM fragments."""
        text = answer.strip()
        if len(text) < 80:  # Lowered threshold for shorter responses
            return True
        if text[-1] not in ".!?✅🌾🌱💧":
            return True
        return False


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
        """Generate response when no relevant documents found — try Gemini first"""
        if self.gemini_service and self.gemini_service.is_available():
            try:
                return self._call_gemini(
                    user_message,
                    context_text="No specific documents matched in the Agrovee knowledge base for this query. Use your general agricultural expertise to help.",
                    extra_context=""
                )
            except Exception as e:
                logger.error(f"Gemini fallback failed: {e}")

        return self._static_fallback_response()

    def _template_response(self, user_message: str, retrieved_docs: List[Dict], context: Optional[Dict]) -> str:
        """Question-specific response used when Gemini is unavailable."""
        if not retrieved_docs:
            return self._static_fallback_response()

        top_doc = retrieved_docs[0]
        response = f"🌱 {top_doc['answer']}"

        # Add context reminder (condensed and helpful)
        if context and (context.get("crop") or context.get("disease")):
            context_parts = []
            if context.get("crop"):
                context_parts.append(f"**{context['crop']}**")
            if context.get("disease"):
                disease_name = context["disease"].replace("_", " ").title()
                context_parts.append(f"*{disease_name}*")
            if context.get("risk"):
                context_parts.append(f"Risk: {context['risk']}")
            
            if context_parts:
                response += f"\n\n*This advice is for {', '.join(context_parts)}.*"

        return response.strip()

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
