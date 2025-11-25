import time
from typing import Dict, Any, List, Optional
from observability.logger import app_logger
from observability.metrics import metrics_collector

class PlanningAgent:
    """
    Planning agent that breaks down learning goals into actionable steps.
    Coordinates with other agents to create comprehensive study plans.
    """
    
    def __init__(self):
        self.name = "PlanningAgent"
    
    def execute(self, user_goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a structured learning plan based on user goals.
        
        Args:
            user_goal: User's learning objective
            context: Optional context with user preferences and history
        
        Returns:
            Structured learning plan
        """
        
        start_time = time.time()
        
        try:
            app_logger.log_agent_action(self.name, "create_plan", user_goal)
            
            parsed_goal = self._parse_learning_goal(user_goal, context)
            
            plan_steps = self._create_plan_steps(parsed_goal)
            
            timeline = self._create_timeline(plan_steps, parsed_goal.get("duration_weeks", 4))
            
            resources_needed = self._identify_resources(parsed_goal)
            
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_agent_execution(self.name, duration_ms)
            
            result = {
                "success": True,
                "agent": self.name,
                "parsed_goal": parsed_goal,
                "plan_steps": plan_steps,
                "timeline": timeline,
                "resources": resources_needed,
                "duration_ms": duration_ms
            }
            
            app_logger.log_agent_action(
                self.name,
                "create_plan",
                user_goal,
                f"Created {len(plan_steps)} step plan",
                duration_ms
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            app_logger.log_error("planning_error", str(e), {"goal": user_goal})
            metrics_collector.record_error("planning_error")
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "duration_ms": duration_ms
            }
    
    def _parse_learning_goal(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Parse the learning goal into structured components."""
        
        goal_lower = goal.lower()
        
        subject = "general"
        if any(word in goal_lower for word in ["math", "calculus", "algebra", "geometry"]):
            subject = "mathematics"
        elif any(word in goal_lower for word in ["program", "code", "python", "javascript"]):
            subject = "programming"
        elif any(word in goal_lower for word in ["science", "physics", "chemistry", "biology"]):
            subject = "science"
        elif any(word in goal_lower for word in ["language", "spanish", "french", "english"]):
            subject = "language"
        elif any(word in goal_lower for word in ["history", "historical"]):
            subject = "history"
        
        level = "beginner"
        if any(word in goal_lower for word in ["advanced", "expert", "master"]):
            level = "advanced"
        elif any(word in goal_lower for word in ["intermediate", "improve", "better"]):
            level = "intermediate"
        
        duration_weeks = 4
        if "week" in goal_lower:
            words = goal_lower.split()
            for i, word in enumerate(words):
                if "week" in word and i > 0:
                    try:
                        duration_weeks = int(words[i-1])
                    except:
                        pass
        elif "month" in goal_lower:
            duration_weeks = 8
        
        hours_per_week = 5
        if "hour" in goal_lower:
            words = goal_lower.split()
            for i, word in enumerate(words):
                if "hour" in word and i > 0:
                    try:
                        hours_per_week = int(words[i-1])
                    except:
                        pass
        
        return {
            "original_goal": goal,
            "subject": subject,
            "level": level,
            "duration_weeks": duration_weeks,
            "hours_per_week": hours_per_week,
            "context": context or {}
        }
    
    def _create_plan_steps(self, parsed_goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create actionable steps for the learning plan."""
        
        subject = parsed_goal["subject"]
        level = parsed_goal["level"]
        
        steps = [
            {
                "step": 1,
                "phase": "Foundation",
                "action": f"Assess current {subject} knowledge and set specific goals",
                "duration_weeks": 1,
                "tools_needed": ["study_planner", "web_search"]
            },
            {
                "step": 2,
                "phase": "Learning",
                "action": f"Study core {subject} concepts at {level} level",
                "duration_weeks": max(1, parsed_goal["duration_weeks"] - 2),
                "tools_needed": ["web_search", "code_executor"]
            },
            {
                "step": 3,
                "phase": "Practice",
                "action": f"Apply {subject} knowledge through exercises and projects",
                "duration_weeks": 1,
                "tools_needed": ["code_executor", "study_planner"]
            },
            {
                "step": 4,
                "phase": "Review",
                "action": "Review progress and identify areas for improvement",
                "duration_weeks": 1,
                "tools_needed": ["study_planner"]
            }
        ]
        
        return steps
    
    def _create_timeline(self, steps: List[Dict[str, Any]], total_weeks: int) -> Dict[str, Any]:
        """Create a timeline for the learning plan."""
        
        timeline = {
            "total_weeks": total_weeks,
            "phases": []
        }
        
        current_week = 1
        for step in steps:
            duration = min(step["duration_weeks"], total_weeks - current_week + 1)
            if duration > 0:
                timeline["phases"].append({
                    "phase": step["phase"],
                    "start_week": current_week,
                    "end_week": current_week + duration - 1,
                    "duration_weeks": duration
                })
                current_week += duration
        
        return timeline
    
    def _identify_resources(self, parsed_goal: Dict[str, Any]) -> List[str]:
        """Identify resources needed for the learning plan."""
        
        resources = [
            "Study planner tool for scheduling",
            "Web search for finding learning materials",
            "Code executor for practice (if applicable)"
        ]
        
        subject = parsed_goal["subject"]
        
        if subject == "programming":
            resources.append("Online coding platform (e.g., LeetCode, Codecademy)")
        elif subject == "mathematics":
            resources.append("Math practice platform (e.g., Khan Academy)")
        elif subject == "science":
            resources.append("Educational videos and interactive simulations")
        elif subject == "language":
            resources.append("Language learning app (e.g., Duolingo)")
        
        return resources

planning_agent = PlanningAgent()
