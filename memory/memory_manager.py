import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MemoryManager:
    def __init__(self, memory_file="memory/memory_store.json"):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Could not load memory: {e}")
                return self._create_empty_memory()
        return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict:
        return {
            "sessions": {},
            "user_profiles": {},
            "conversation_history": [],
            "study_plans": {},
            "learning_paths": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def _save_memory(self):
        try:
            self.memory["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Could not save memory: {e}")
    
    def create_session(self, session_id: str, user_data: Optional[Dict] = None) -> Dict:
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "user_data": user_data or {},
            "conversation": [],
            "agent_states": {},
            "active": True
        }
        self.memory["sessions"][session_id] = session
        self._save_memory()
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        session = self.memory["sessions"].get(session_id)
        if session:
            session["last_accessed"] = datetime.now().isoformat()
            self._save_memory()
        return session
    
    def update_session(self, session_id: str, updates: Dict):
        if session_id in self.memory["sessions"]:
            self.memory["sessions"][session_id].update(updates)
            self.memory["sessions"][session_id]["last_accessed"] = datetime.now().isoformat()
            self._save_memory()
    
    def add_to_conversation(self, session_id: str, role: str, content: str):
        if session_id in self.memory["sessions"]:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content
            }
            self.memory["sessions"][session_id]["conversation"].append(entry)
            
            self.memory["conversation_history"].append({
                "session_id": session_id,
                **entry
            })
            
            if len(self.memory["conversation_history"]) > 1000:
                self.memory["conversation_history"] = self.memory["conversation_history"][-1000:]
            
            self._save_memory()
    
    def update_agent_state(self, session_id: str, agent_name: str, state: Dict):
        if session_id in self.memory["sessions"]:
            if "agent_states" not in self.memory["sessions"][session_id]:
                self.memory["sessions"][session_id]["agent_states"] = {}
            
            self.memory["sessions"][session_id]["agent_states"][agent_name] = {
                "state": state,
                "updated_at": datetime.now().isoformat()
            }
            self._save_memory()
    
    def get_agent_state(self, session_id: str, agent_name: str) -> Optional[Dict]:
        session = self.memory["sessions"].get(session_id)
        if session and "agent_states" in session:
            agent_data = session["agent_states"].get(agent_name)
            return agent_data["state"] if agent_data else None
        return None
    
    def save_study_plan(self, user_id: str, plan: Dict):
        if user_id not in self.memory["study_plans"]:
            self.memory["study_plans"][user_id] = []
        
        plan["created_at"] = datetime.now().isoformat()
        self.memory["study_plans"][user_id].append(plan)
        self._save_memory()
    
    def get_study_plans(self, user_id: str) -> List[Dict]:
        return self.memory["study_plans"].get(user_id, [])
    
    def save_learning_path(self, user_id: str, path: Dict):
        self.memory["learning_paths"][user_id] = {
            **path,
            "created_at": datetime.now().isoformat()
        }
        self._save_memory()
    
    def get_learning_path(self, user_id: str) -> Optional[Dict]:
        return self.memory["learning_paths"].get(user_id)
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        if session_id in self.memory["sessions"]:
            conversation = self.memory["sessions"][session_id].get("conversation", [])
            return conversation[-limit:]
        return []
    
    def close_session(self, session_id: str):
        if session_id in self.memory["sessions"]:
            self.memory["sessions"][session_id]["active"] = False
            self.memory["sessions"][session_id]["closed_at"] = datetime.now().isoformat()
            self._save_memory()
    
    def get_all_sessions(self) -> Dict:
        return self.memory["sessions"]
    
    def cleanup_old_sessions(self, days_old: int = 30):
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days_old)
        
        sessions_to_remove = []
        for session_id, session in self.memory["sessions"].items():
            last_accessed = datetime.fromisoformat(session["last_accessed"])
            if last_accessed < cutoff and not session.get("active", False):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.memory["sessions"][session_id]
        
        if sessions_to_remove:
            self._save_memory()
        
        return len(sessions_to_remove)

memory_manager = MemoryManager()
