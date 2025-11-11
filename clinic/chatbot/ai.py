import os
import json
from typing import List, Optional

from django.conf import settings
from django.contrib.auth.models import User
from .ai_agent import AIAgent


def _load_project_corpus() -> List[str]:
    """Load and flatten project/context JSON files into text chunks."""
    base = settings.BASE_DIR
    corpus: List[str] = []

    json_files = [
        os.path.join(base, "chatbot", "project_info.json"),
        os.path.join(base, "chatbot", "hostel_info.json"),
        os.path.join(base, "chatbot", "medical_knowledge.json"),  # Added medical knowledge base
    ]

    for path in json_files:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            corpus.append(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            # Skip unreadable files
            continue

    return corpus


def _build_retriever():
    """Build a retriever. Prefer LangChain + FAISS + sentence-transformers if available.

    Falls back to simple keyword scoring if deps are missing.
    """
    corpus = _load_project_corpus()
    if not corpus:
        return SimpleKeywordRetriever([])

    # Fast mode: skip heavy deps entirely
    if os.environ.get("AI_FAST_MODE", "0") == "1":
        return SimpleKeywordRetriever(corpus)

    try:
        # Lazy imports so project runs without heavy deps
        from langchain_community.vectorstores import FAISS  # type: ignore
        from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
        # Small, CPU-friendly model
        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        docs = [c for c in corpus]
        # Build FAISS index
        vectordb = FAISS.from_texts(docs, embedding)

        class FaissRetriever:
            def __init__(self, db):
                self.db = db

            def get_top_k(self, query: str, k: int = 3) -> List[str]:
                results = self.db.similarity_search(query, k=k)
                return [r.page_content for r in results]

        return FaissRetriever(vectordb)
    except Exception:
        return SimpleKeywordRetriever(corpus)


class SimpleKeywordRetriever:
    """Very lightweight fallback retriever using keyword overlap scoring."""

    def __init__(self, documents: List[str]):
        self.documents = documents

    def get_top_k(self, query: str, k: int = 3) -> List[str]:
        if not self.documents:
            return []
        terms = set(query.lower().split())
        scored = []
        for doc in self.documents:
            text = doc.lower()
            score = sum(1 for t in terms if t in text)
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:k]]


_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = _build_retriever()
    return _retriever


def _generate_with_hfhub(prompt: str) -> Optional[str]:
    """Try using Hugging Face Inference API via langchain if token is set.

    Returns text or None if unavailable.
    """
    token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        return None
    try:
        # Lazy import
        from langchain_community.llms import HuggingFaceHub  # type: ignore
        llm = HuggingFaceHub(
            repo_id="google/flan-t5-base",
            huggingfacehub_api_token=token,
            model_kwargs={"temperature": 0.7, "max_length": 512},  # Increased temperature for more creative responses
        )
        return llm(prompt)
    except Exception:
        return None


def _generate_locally(prompt: str) -> Optional[str]:
    """Try a very small local HF model. Returns None if deps missing."""
    # Only run if explicitly enabled to avoid long cold-starts
    if os.environ.get("ENABLE_LOCAL_LLM", "0") != "1":
        return None
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore
        import torch  # type: ignore

        model_id = "google/flan-t5-small"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=300)  # Increased token limit
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception:
        return None


def answer_question(user_query: str, user: User = None) -> str:
    """Answer a query using RAG over local project data, with optional HF generation."""
    # If we have a user, use the AI Agent for enhanced functionality
    if user:
        agent = AIAgent(user)
        result = agent.process_command(user_query)
        
        # If the agent handled the request, return the result
        if isinstance(result, dict) and "success" in result:
            if result.get("success", False):
                if "patients" in result:
                    patient_list = "\n".join([f"- {p['first_name']} {p['last_name']} (ID: {p['id']})" for p in result["patients"]])
                    return f"Here are your patients:\n{patient_list}"
                elif "feedback" in result:
                    feedback_list = "\n".join([f"- From {f['from']}: {f['subject']} ({f['timestamp']})" for f in result["feedback"]])
                    return f"Your recent messages:\n{feedback_list}"
                elif "appointments" in result:
                    appt_list = "\n".join([f"- {a['date']} at {a['time']}: {a['reason']} (Status: {a['status']})" for a in result["appointments"]])
                    return f"Your appointments:\n{appt_list}"
                elif "history" in result:
                    history_list = "\n".join([f"- {h['disease_type']}: {h['result']} ({h['confidence']}) on {h['date']}" for h in result["history"]])
                    return f"Prediction history:\n{history_list}"
            else:
                return result.get("message", "I couldn't process that request.")
        elif isinstance(result, dict) and "action" in result:
            return result.get("message", "I can help with that. What information do you need?")
    
    # Fall back to original RAG approach for medical queries
    retriever = _get_retriever()
    top_docs = retriever.get_top_k(user_query, k=3)

    context = "\n\n".join(top_docs) if top_docs else ""

    # Enhanced system prompt for medical queries
    system_prompt = (
        "You are an AI medical assistant for a Django healthcare + hostel project. "
        "Answer accurately based on the provided context. For medical questions, provide helpful, "
        "detailed information while emphasizing this is for educational purposes only. "
        "Always include a disclaimer for medical questions. "
        "If the question is unrelated to the context, provide a general helpful response. "
        "Focus on generating new, unique responses rather than static answers. "
        "Use the medical knowledge base to provide comprehensive information about conditions, symptoms, "
        "risk factors, and prevention strategies when relevant."
    )
    
    # Enhanced prompt with better structure for medical queries
    prompt = (
        f"{system_prompt}\n\n"
        f"Knowledge Base Information:\n{context}\n\n"
        f"User Question: {user_query}\n\n"
        f"Please provide a comprehensive, unique response tailored to this specific question. "
        f"For medical questions, be detailed but emphasize this is educational information only. "
        f"Structure your response with clear headings and bullet points where appropriate.\n"
        f"Response:"
    )

    # Prefer HF Inference API if configured
    text = _generate_with_hfhub(prompt)
    if not text:
        # Try local tiny model if explicitly enabled
        text = _generate_locally(prompt)

    if not text:
        # Fallback: extractive-style answer from context
        if context:
            snippet = context[:900]
            return (
                f"Based on available information: \n{snippet}\n\n"
                f"For medical questions: This is general information only and not medical advice. "
                f"Please consult with a healthcare professional for personalized medical advice."
            )
        return (
            "I couldn't load AI models on this server. Please set HUGGINGFACEHUB_API_TOKEN or install transformers/torch. "
            "Meanwhile, ask about project features and I will answer from the built-in guide."
        )

    # Enhance the response for medical queries
    lower_q = user_query.lower()
    medical_keywords = ["medical", "medicine", "symptom", "treat", "doctor", "health", "disease", "diagnos", 
                       "condition", "pain", "therapy", "medication", "prescription", "illness", "disorder",
                       "injury", "recovery", "prevention", "vaccine", "immunization", "allergy", "infection"]
    
    if any(w in lower_q for w in medical_keywords):
        # Add a more comprehensive disclaimer for medical queries
        text += ("\n\n⚕️ IMPORTANT MEDICAL DISCLAIMER: This information is for educational purposes only "
                "and should not be considered medical advice. Always consult with a qualified healthcare "
                "professional for diagnosis, treatment, or medical advice. Do not disregard professional "
                "medical advice or delay seeking it based on information provided here.")
    elif "health" in lower_q:
        # Add a lighter disclaimer for general health queries
        text += ("\n\n⚕️ Note: This is general health information only. For specific health concerns, "
                "please consult with a healthcare professional.")
    
    return text