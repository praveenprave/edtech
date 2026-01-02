import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from app.services.rag import RAGService

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-pro") # Configurable Model
FAST_MODEL_NAME = os.getenv("FAST_MODEL_NAME", "gemini-1.5-flash") # Configurable Fast Model

# Initialize Vertex AI
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"⚠️ Vertex AI Init failed (Mocking mode possibly): {e}")

class Agent:
    def __init__(self, model_name=None, system_instruction=""):
        # Use env var if no specific model passed
        self.model = GenerativeModel(
            model_name or MODEL_NAME,
            system_instruction=system_instruction
        )

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
             return f"Error generating content: {e}"

class ResearchAgent(Agent):
    def __init__(self):
        super().__init__(
            model_name=MODEL_NAME, # Uses Config
            system_instruction="""You are an expert Academic Researcher.
            Your job is to answer the user's query STRICTLY based on the provided RAG Context.
            Do not hallucinate. Cite the textbook page numbers if available.
            Input: User Query + RAG Context.
            Output: A structured Fact Brief."""
        )
        self.rag = RAGService(project_id=PROJECT_ID)

    from typing import List, Dict
    def research(self, query: str, history: List[dict] = []) -> str:
        # 1. Rewrite Query if needed (Contextual RAG)
        search_query = self._rewrite_query(query, history)
        
        # 2. Retrieve from Vector DB
        context = self.rag.search(search_query)
        
        # 3. Synthesize with Gemini (with History)
        history_text = ""
        if history:
             for turn in history[-3:]:
                 role = turn.get("role", "user")
                 content = turn.get("content", "")
                 history_text += f"{role}: {content}\n"

        prompt = f"""
        You are an expert Tutor. Answer the query based on the Context and Conversation History.
        
        Conversation History:
        {history_text}
        
        Current Query: {query}
        
        Retrieved Textbook Context:
        {context}
        
        Task: Provide a helpful, accurate answer.
        If the query is "explain more", use the history to understand what to explain.
        """
        return self.generate(prompt)

    def _rewrite_query(self, query: str, history: List[dict]) -> str:
        """
        Rewrites the user query to be standalone based on history.
        """
        if not history:
            return query
            
        # Quick check for context-dependent queries
        # In production, use an LLM call here. 
        # For efficiency, we'll try a simple heuristic or a fast LLM call.
        
        # Heuristic: If query length < 15 chars and history exists, likely dependent.
        if len(query) < 20 or "explain" in query.lower() or "what is it" in query.lower():
             # Use the Model to rewrite (Cost checking: negligible for this demo)
             prompt = f"""
             Rewrite the last user query to be a standalone search query based on history.
             History: {history[-1].get('content')}
             Last Query: {query}
             Standalone Query:"""
             
             # We can use the base agent's generate, but it might be overkill. 
             # Let's just append the previous user message for now as a naive "rewrite"
             # Better: "Previous Topic + Current Query"
             
             # Naive Fallback for speed: 
             # If "explain more", append previous user query.
             last_user_msg = next((m['content'] for m in reversed(history) if m['role'] == 'user'), "")
             print(f"🔄 Rewriting Query: '{query}' using context '{last_user_msg[:20]}...'")
             return f"{last_user_msg} {query}"
             
        return query

class ScriptwriterAgent(Agent):
    def __init__(self):
        super().__init__(
            model_name=MODEL_NAME, # Uses Config
            system_instruction="""You are a Pedagogical Scriptwriter.
            Convert the Fact Brief into an engaging Video Script.
            
            Structure:
            - **Intro** (0-30s): Hook the student. (Speaker: Avatar)
            - **Concept** (30s-2m): Explain the core concept with visual analogies. (Speaker: Narration + Visuals)
            - **Examples** (2m-3m): Real-world application.
            - **Summary**: Quick recap.
            
            Format: Use a Split-Script format (Audio | Visual)."""
        )

class ValidationAgent(Agent):
    def __init__(self):
        super().__init__(
            model_name=FAST_MODEL_NAME, # Uses Config (Flash)
            system_instruction="""You are the Quality Control Officer.
            Verify that the script aligns with the RAG Fact Brief.
            Check for:
            1. Factual Accuracy (Does it contradict the textbook?)
            2. Age Appropriateness (Is language simple?)
            3. Safety (No dangerous chemicals/experiments without warning).
            
            Output: "APPROVED" or "REJECTED: <Reason>"."""
        )
