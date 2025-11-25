import os
import time
from typing import Dict, Any, List, Optional
from observability.logger import app_logger
from observability.metrics import metrics_collector

MODEL_NAME = "gemini-2.5-flash"

try:
    import google.genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GENAI_AVAILABLE = True
    except ImportError:
        genai = None
        GENAI_AVAILABLE = False

class LLMAgent:
    """
    LLM-powered agent using Google's Gemini API.
    Handles natural language understanding and generation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "LLMAgent"
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = None
        self._initialized = False
        
        self.system_prompt = """You are an educational AI assistant specialized in helping students create personalized study plans and learning paths. 

Your role is to:
- Understand student goals and learning preferences
- Provide educational guidance and resources
- Help break down complex topics into manageable steps
- Encourage effective learning strategies
- Be supportive and motivating

Keep responses concise, practical, and focused on education."""
        
        if not GENAI_AVAILABLE:
            print("Warning: google-generativeai package not available. LLM features will be disabled.")
            return
        
        if self.api_key:
            try:
                # Try new SDK first
                try:
                    import google.genai
                    google.genai.configure(api_key=self.api_key)
                    self.model = google.genai.GenerativeModel(MODEL_NAME)
                    self._initialized = True
                except:
                    # Fallback to older SDK
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.model = genai.GenerativeModel(MODEL_NAME)
                    self._initialized = True
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
    
    def execute(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user input and generate response using Gemini.
        
        Args:
            user_input: User's message or query
            context: Optional context including conversation history
        
        Returns:
            Agent response with generated content
        """
        
        start_time = time.time()
        
        if not self._initialized or not self.model:
            return {
                "success": False,
                "agent": self.name,
                "error": "GOOGLE_API_KEY not configured. Please add your API key to use LLM features.",
                "user_input": user_input,
                "duration_ms": 0
            }
        
        try:
            prompt = self._build_prompt(user_input, context)
            
            app_logger.log_agent_action(
                self.name,
                "generate_response",
                user_input[:100]
            )
            
            response = self.model.generate_content(prompt)
            
            duration_ms = (time.time() - start_time) * 1000
            
            metrics_collector.record_agent_execution(self.name, duration_ms)
            
            result = {
                "success": True,
                "agent": self.name,
                "response": response.text,
                "user_input": user_input,
                "duration_ms": duration_ms
            }
            
            app_logger.log_agent_action(
                self.name,
                "generate_response",
                user_input[:100],
                response.text[:100],
                duration_ms
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            app_logger.log_error("llm_generation_error", str(e), {"input": user_input})
            metrics_collector.record_error("llm_error")
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "user_input": user_input,
                "duration_ms": duration_ms
            }
    
    def _build_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        """Build the full prompt with system instructions and context."""
        
        prompt_parts = [self.system_prompt, ""]
        
        if context and "conversation_history" in context:
            prompt_parts.append("Previous conversation:")
            for msg in context["conversation_history"][-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("")
        
        if context and "user_profile" in context:
            profile = context["user_profile"]
            prompt_parts.append(f"Student Profile: {profile}")
            prompt_parts.append("")
        
        prompt_parts.append(f"User: {user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def analyze_learning_needs(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to extract learning needs and preferences.
        
        Args:
            user_input: User's description of what they want to learn
        
        Returns:
            Structured analysis of learning needs
        """
        
        if not self._initialized or not self.model:
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not configured",
                "original_input": user_input
            }
        
        analysis_prompt = f"""Analyze this student's learning request and extract key information:

"{user_input}"

Provide a structured analysis in this format:
- Subject: [main topic]
- Level: [beginner/intermediate/advanced]
- Duration: [estimated weeks needed]
- Learning Style: [visual/auditory/reading/kinesthetic/mixed]
- Goals: [specific learning objectives]

Be concise and specific."""
        
        try:
            response = self.model.generate_content(analysis_prompt)
            
            return {
                "success": True,
                "analysis": response.text,
                "original_input": user_input
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_input": user_input
            }
    
    def generate_study_recommendations(self, subject: str, level: str, 
                                      context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate study recommendations for a specific subject and level.
        
        Args:
            subject: Subject to study
            level: Skill level
            context: Additional context
        
        Returns:
            Study recommendations
        """
        
        if not self._initialized or not self.model:
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not configured"
            }
        
        prompt = f"""Provide specific study recommendations for learning {subject} at {level} level.
        
{f'Additional context: {context}' if context else ''}

Include:
1. Key concepts to master
2. Recommended study approach
3. Common pitfalls to avoid
4. Success metrics

Keep it practical and actionable."""
        
        try:
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "subject": subject,
                "level": level,
                "recommendations": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

_llm_agent_instance = None

def get_llm_agent():
    """Get or create the LLM agent instance (lazy initialization)."""
    global _llm_agent_instance
    if _llm_agent_instance is None:
        _llm_agent_instance = LLMAgent()
    return _llm_agent_instance
