import time
from typing import Dict, Any, List, Optional
from agents.llm_agent import get_llm_agent
from agents.planning_agent import planning_agent
from agents.loop_agent import loop_agent
from tools.custom_tool import study_planner_tool
from tools.code_exec_tool import code_executor_tool
from tools.search_tool import web_search_tool
from services.session_service import session_service
from memory.memory_manager import memory_manager
from observability.logger import app_logger
from observability.metrics import metrics_collector

class AgentOrchestrator:
    """
    Orchestrates multiple agents to work together on user requests.
    Manages sequential execution flow and agent coordination.
    """
    
    def __init__(self):
        self._llm_agent = None
        self.agents = {
            "planning": planning_agent,
            "loop": loop_agent
        }
        
        self.tools = {
            "study_planner": study_planner_tool,
            "code_executor": code_executor_tool,
            "web_search": web_search_tool
        }
    
    def _get_llm(self):
        """Get LLM agent instance with lazy initialization."""
        if self._llm_agent is None:
            self._llm_agent = get_llm_agent()
        return self._llm_agent
    
    def process_request(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user request through the agent system.
        
        Args:
            user_input: User's request or query
            session_id: Optional session identifier
        
        Returns:
            Orchestrated response from agents
        """
        
        start_time = time.time()
        
        if not session_id:
            session_id = session_service.create_session()
        
        session_service.add_message(session_id, "user", user_input)
        
        app_logger.log_event("orchestration_start", {
            "session_id": session_id,
            "input": user_input[:100]
        })
        
        try:
            request_type = self._classify_request(user_input)
            
            if request_type == "create_study_plan":
                result = self._handle_study_plan_request(user_input, session_id)
            elif request_type == "ask_question":
                result = self._handle_question(user_input, session_id)
            elif request_type == "execute_code":
                result = self._handle_code_execution(user_input, session_id)
            elif request_type == "search_info":
                result = self._handle_search(user_input, session_id)
            else:
                result = self._handle_general_request(user_input, session_id)
            
            session_service.add_message(session_id, "assistant", str(result.get("response", "")))
            
            duration_ms = (time.time() - start_time) * 1000
            
            result["session_id"] = session_id
            result["duration_ms"] = duration_ms
            
            app_logger.log_event("orchestration_complete", {
                "session_id": session_id,
                "duration_ms": duration_ms,
                "success": result.get("success", False)
            })
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            app_logger.log_error("orchestration_error", str(e), {"session_id": session_id})
            metrics_collector.record_error("orchestration_error")
            
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "duration_ms": duration_ms
            }
    
    def _classify_request(self, user_input: str) -> str:
        """Classify the type of user request."""
        
        lower_input = user_input.lower()
        
        plan_keywords = ["study plan", "learning plan", "help me learn", "want to study", 
                        "create plan", "schedule", "learn"]
        question_keywords = ["what is", "how do", "explain", "tell me about", "?"]
        code_keywords = ["calculate", "compute", "run code", "execute", "python"]
        search_keywords = ["search", "find information", "look up", "research"]
        
        if any(kw in lower_input for kw in plan_keywords):
            return "create_study_plan"
        elif any(kw in lower_input for kw in code_keywords):
            return "execute_code"
        elif any(kw in lower_input for kw in search_keywords):
            return "search_info"
        elif any(kw in lower_input for kw in question_keywords):
            return "ask_question"
        else:
            return "general"
    
    def _handle_study_plan_request(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle study plan creation request."""
        
        conversation_history = session_service.get_conversation_history(session_id, limit=5)
        
        llm_result = self._get_llm().analyze_learning_needs(user_input)
        
        llm_analysis = llm_result if llm_result.get("success", False) else None
        
        planning_result = self.agents["planning"].execute(user_input, {
            "conversation_history": conversation_history,
            "llm_analysis": llm_analysis
        })
        
        if planning_result["success"]:
            parsed_goal = planning_result["parsed_goal"]
            
            study_plan = self.tools["study_planner"].execute(
                subject=parsed_goal.get("subject", "general"),
                duration_weeks=parsed_goal.get("duration_weeks", 4),
                level=parsed_goal.get("level", "beginner"),
                hours_per_week=parsed_goal.get("hours_per_week", 5),
                learning_style="mixed"
            )
            
            metrics_collector.record_tool_call("study_planner", success=True)
            app_logger.log_tool_call("study_planner", user_input, study_plan)
            
            refinement_result = self.agents["loop"].refine_until_quality(
                "refine_study_plan",
                study_plan,
                target_quality=85
            )
            
            final_plan = refinement_result["final_result"]["output"] if refinement_result["success"] else study_plan
            
            memory_manager.save_study_plan(
                session_service.get_session(session_id).get("user_id", "anonymous"),
                final_plan
            )
            
            context = {
                "conversation_history": conversation_history,
                "study_plan": final_plan
            }
            
            response_result = self._get_llm().execute(
                f"I've created a study plan for: {user_input}. Please provide a friendly summary.",
                context
            )
            
            if not response_result.get("success", False):
                response_text = f"I've created a personalized study plan for {parsed_goal.get('subject', 'your topic')}! Check the study plan details below. (Note: AI summary unavailable - please add GOOGLE_API_KEY for enhanced responses)"
            else:
                response_text = response_result.get("response", "Study plan created successfully!")
            
            return {
                "success": True,
                "response": response_text,
                "study_plan": final_plan,
                "planning_details": planning_result,
                "refinement_iterations": refinement_result.get("total_iterations", 0),
                "agents_used": ["llm", "planning", "loop"],
                "tools_used": ["study_planner"],
                "llm_available": response_result.get("success", False)
            }
        
        return {
            "success": False,
            "response": "Could not create study plan",
            "error": planning_result.get("error")
        }
    
    def _handle_question(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle question answering request."""
        
        conversation_history = session_service.get_conversation_history(session_id, limit=10)
        
        search_result = self.tools["web_search"].execute(user_input)
        metrics_collector.record_tool_call("web_search", success=search_result["success"])
        app_logger.log_tool_call("web_search", user_input, search_result)
        
        context = {
            "conversation_history": conversation_history,
            "search_results": search_result
        }
        
        llm_result = self._get_llm().execute(user_input, context)
        
        if not llm_result.get("success", False):
            if search_result.get("success", False):
                response_text = f"Based on my search: {search_result.get('summary', 'Information found.')} (Note: AI summary unavailable - please add GOOGLE_API_KEY for enhanced answers)"
            else:
                return {
                    "success": False,
                    "response": "Could not answer question. Both LLM and search failed.",
                    "error": llm_result.get("error", "Unknown error")
                }
        else:
            response_text = llm_result.get("response", "")
        
        return {
            "success": True,
            "response": response_text,
            "search_results": search_result,
            "agents_used": ["llm"],
            "tools_used": ["web_search"],
            "llm_available": llm_result.get("success", False)
        }
    
    def _handle_code_execution(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle code execution request."""
        
        code = self._extract_code_from_input(user_input)
        
        if not code:
            return {
                "success": False,
                "response": "No code found to execute",
                "error": "No code provided"
            }
        
        exec_result = self.tools["code_executor"].execute(code)
        metrics_collector.record_tool_call("code_executor", success=exec_result["success"])
        app_logger.log_tool_call("code_executor", code, exec_result)
        
        conversation_history = session_service.get_conversation_history(session_id, limit=5)
        
        context = {
            "conversation_history": conversation_history,
            "execution_result": exec_result
        }
        
        llm_result = self._get_llm().execute(
            f"Explain this code execution result: {exec_result.get('output', '')}",
            context
        )
        
        if not llm_result.get("success", False):
            if exec_result["success"]:
                response_text = f"Code executed successfully. Output: {exec_result.get('output', 'No output')} (Note: AI explanation unavailable - please add GOOGLE_API_KEY for enhanced responses)"
            else:
                response_text = f"Code execution failed: {exec_result.get('error', 'Unknown error')}"
        else:
            response_text = llm_result.get("response", "")
        
        return {
            "success": exec_result["success"],
            "response": response_text,
            "execution_result": exec_result,
            "agents_used": ["llm"],
            "tools_used": ["code_executor"],
            "llm_available": llm_result.get("success", False)
        }
    
    def _handle_search(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle search request."""
        
        search_result = self.tools["web_search"].search_educational_content(user_input)
        metrics_collector.record_tool_call("web_search", success=search_result["success"])
        app_logger.log_tool_call("web_search", user_input, search_result)
        
        return {
            "success": search_result["success"],
            "response": search_result.get("summary", "No results found"),
            "search_results": search_result,
            "tools_used": ["web_search"]
        }
    
    def _handle_general_request(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle general request."""
        
        conversation_history = session_service.get_conversation_history(session_id, limit=10)
        
        context = {
            "conversation_history": conversation_history
        }
        
        llm_result = self._get_llm().execute(user_input, context)
        
        if not llm_result.get("success", False):
            return {
                "success": False,
                "response": "I need the GOOGLE_API_KEY to answer general questions. Please add your API key to enable AI-powered responses. You can still use other features like study planning (without AI summaries), code execution, and web search!",
                "error": llm_result.get("error", "LLM not available"),
                "agents_used": ["llm"],
                "llm_available": False
            }
        
        return {
            "success": True,
            "response": llm_result.get("response", ""),
            "agents_used": ["llm"],
            "llm_available": True
        }
    
    def _extract_code_from_input(self, user_input: str) -> Optional[str]:
        """Extract code from user input."""
        
        if "```python" in user_input:
            parts = user_input.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()
        
        if "```" in user_input:
            parts = user_input.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        
        code_keywords = ["print(", "def ", "for ", "while ", "if "]
        if any(kw in user_input for kw in code_keywords):
            return user_input
        
        return None

orchestrator = AgentOrchestrator()
