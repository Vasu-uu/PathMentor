import uuid
from typing import Dict, Optional, Any
from datetime import datetime
from memory.memory_manager import memory_manager
from observability.logger import app_logger
from observability.metrics import metrics_collector

class SessionService:
    """
    Manages user sessions and state across agent interactions.
    """
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, user_id: Optional[str] = None, 
                      user_data: Optional[Dict] = None) -> str:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            user_data: Optional user profile data
        
        Returns:
            Session ID
        """
        
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id or "anonymous",
            "user_data": user_data or {},
            "created_at": datetime.now().isoformat()
        }
        
        memory_manager.create_session(session_id, session_data)
        
        self.active_sessions[session_id] = {
            "session_id": session_id,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        metrics_collector.record_session_event("created")
        app_logger.log_session_event(session_id, "created", session_data)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None
        """
        
        session = memory_manager.get_session(session_id)
        
        if session:
            app_logger.log_session_event(session_id, "accessed", {})
        
        return session
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates
        
        Returns:
            Success status
        """
        
        try:
            memory_manager.update_session(session_id, updates)
            app_logger.log_session_event(session_id, "updated", updates)
            return True
        except Exception as e:
            app_logger.log_error("session_update_error", str(e), {"session_id": session_id})
            return False
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Add a message to session conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
        
        Returns:
            Success status
        """
        
        try:
            memory_manager.add_to_conversation(session_id, role, content)
            return True
        except Exception as e:
            app_logger.log_error("add_message_error", str(e), {"session_id": session_id})
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> list:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
        
        Returns:
            List of conversation messages
        """
        
        return memory_manager.get_conversation_history(session_id, limit)
    
    def update_agent_state(self, session_id: str, agent_name: str, state: Dict):
        """
        Update agent-specific state for a session.
        
        Args:
            session_id: Session identifier
            agent_name: Agent name
            state: Agent state data
        """
        
        memory_manager.update_agent_state(session_id, agent_name, state)
        app_logger.log_session_event(
            session_id, 
            "agent_state_updated", 
            {"agent": agent_name}
        )
    
    def get_agent_state(self, session_id: str, agent_name: str) -> Optional[Dict]:
        """
        Get agent-specific state for a session.
        
        Args:
            session_id: Session identifier
            agent_name: Agent name
        
        Returns:
            Agent state or None
        """
        
        return memory_manager.get_agent_state(session_id, agent_name)
    
    def close_session(self, session_id: str):
        """
        Close a session.
        
        Args:
            session_id: Session identifier
        """
        
        memory_manager.close_session(session_id)
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["active"] = False
        
        metrics_collector.record_session_event("closed")
        app_logger.log_session_event(session_id, "closed", {})
    
    def list_active_sessions(self) -> Dict:
        """
        List all active sessions.
        
        Returns:
            Dictionary of active sessions
        """
        
        return {
            sid: data 
            for sid, data in self.active_sessions.items() 
            if data.get("active", False)
        }
    
    def get_all_sessions(self) -> list:
        """
        Get all sessions with their first message for chat history sidebar.
        
        Returns:
            List of session data with preview
        """
        try:
            sessions_dict = memory_manager.get_all_sessions()
            sessions_list = []
            
            for session_id, session_data in sessions_dict.items():
                conversation = session_data.get("conversation", [])
                first_message = ""
                
                if conversation:
                    for msg in conversation:
                        if msg.get("role") == "user":
                            first_message = msg.get("content", "")
                            break
                
                sessions_list.append({
                    "session_id": session_id,
                    "first_message": first_message,
                    "created_at": session_data.get("created_at")
                })
            
            # Sort by creation time, newest first
            sessions_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return sessions_list
        except Exception as e:
            app_logger.log_error("get_all_sessions_error", str(e))
            return []

session_service = SessionService()
