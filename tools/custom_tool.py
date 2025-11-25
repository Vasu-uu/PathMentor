import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class StudyPlannerTool:
    """
    Custom tool for educational study planning.
    Creates personalized study schedules and resource recommendations.
    """
    
    def __init__(self):
        self.name = "study_planner"
        self.description = "Creates personalized study plans based on subject, duration, and learning goals"
        
        self.subject_resources = {
            "mathematics": {
                "beginner": ["Khan Academy", "Basic Math Textbook", "Math is Fun"],
                "intermediate": ["Coursera Calculus", "MIT OpenCourseWare", "Paul's Online Math Notes"],
                "advanced": ["Advanced Calculus Books", "Research Papers", "Mathematical Proofs"]
            },
            "programming": {
                "beginner": ["Codecademy", "Python.org Tutorial", "FreeCodeCamp"],
                "intermediate": ["LeetCode", "Real Python", "Full Stack Open"],
                "advanced": ["System Design", "Advanced Algorithms", "Open Source Projects"]
            },
            "science": {
                "beginner": ["Khan Academy Science", "Crash Course", "Science Buddies"],
                "intermediate": ["Coursera Science Courses", "Scientific American", "Nature Education"],
                "advanced": ["Research Papers", "Advanced Textbooks", "Lab Experiences"]
            },
            "language": {
                "beginner": ["Duolingo", "Basic Grammar Books", "Language Apps"],
                "intermediate": ["iTalki", "Native Content", "Language Exchange"],
                "advanced": ["Literature", "Academic Writing", "Professional Translation"]
            },
            "history": {
                "beginner": ["Crash Course History", "History.com", "Simple Timelines"],
                "intermediate": ["Academic Textbooks", "Documentary Series", "Primary Sources"],
                "advanced": ["Research Papers", "Historical Archives", "Specialized Studies"]
            }
        }
    
    def execute(self, subject: str, duration_weeks: int, level: str = "beginner", 
                hours_per_week: int = 5, learning_style: str = "mixed") -> Dict[str, Any]:
        """
        Generate a personalized study plan.
        
        Args:
            subject: The subject to study
            duration_weeks: How many weeks to study
            level: Skill level (beginner, intermediate, advanced)
            hours_per_week: Weekly study hours
            learning_style: Learning preference (visual, auditory, reading, kinesthetic, mixed)
        
        Returns:
            Detailed study plan with schedule and resources
        """
        
        subject_lower = subject.lower()
        
        if subject_lower not in self.subject_resources:
            subject_lower = "programming"
        
        resources = self.subject_resources[subject_lower].get(level, 
                                                               self.subject_resources[subject_lower]["beginner"])
        
        weekly_schedule = self._create_weekly_schedule(hours_per_week, learning_style)
        
        milestones = self._create_milestones(subject, duration_weeks, level)
        
        study_plan = {
            "subject": subject,
            "level": level,
            "duration_weeks": duration_weeks,
            "hours_per_week": hours_per_week,
            "learning_style": learning_style,
            "total_hours": duration_weeks * hours_per_week,
            "weekly_schedule": weekly_schedule,
            "recommended_resources": resources,
            "milestones": milestones,
            "study_tips": self._get_study_tips(learning_style),
            "created_at": datetime.now().isoformat()
        }
        
        return study_plan
    
    def _create_weekly_schedule(self, hours_per_week: int, learning_style: str) -> List[Dict]:
        """Create a weekly study schedule."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        sessions_per_week = min(hours_per_week, 7)
        hours_per_session = hours_per_week / sessions_per_week
        
        schedule = []
        for i in range(sessions_per_week):
            day = days[i]
            
            if learning_style == "visual":
                activity = "Watch video lectures and diagram practice"
            elif learning_style == "auditory":
                activity = "Listen to podcasts and discuss concepts"
            elif learning_style == "reading":
                activity = "Read textbooks and take notes"
            elif learning_style == "kinesthetic":
                activity = "Hands-on practice and experiments"
            else:
                activities = ["Watch lectures", "Practice problems", "Read materials", "Hands-on work"]
                activity = activities[i % len(activities)]
            
            schedule.append({
                "day": day,
                "duration_hours": round(hours_per_session, 1),
                "activity": activity,
                "recommended_time": "Morning" if i < 3 else "Evening"
            })
        
        return schedule
    
    def _create_milestones(self, subject: str, duration_weeks: int, level: str) -> List[Dict]:
        """Create learning milestones."""
        milestones = []
        
        weeks_per_milestone = max(1, duration_weeks // 4)
        
        if level == "beginner":
            milestone_names = [
                f"Understand basic {subject} concepts",
                f"Complete introductory {subject} exercises",
                f"Apply {subject} to simple problems",
                f"Master fundamental {subject} skills"
            ]
        elif level == "intermediate":
            milestone_names = [
                f"Review and strengthen {subject} fundamentals",
                f"Tackle intermediate {subject} challenges",
                f"Build {subject} projects",
                f"Achieve proficiency in {subject}"
            ]
        else:
            milestone_names = [
                f"Explore advanced {subject} topics",
                f"Research {subject} specialization areas",
                f"Contribute to {subject} community",
                f"Master expert-level {subject} concepts"
            ]
        
        for i, name in enumerate(milestone_names):
            week_num = (i + 1) * weeks_per_milestone
            if week_num <= duration_weeks:
                milestones.append({
                    "week": week_num,
                    "milestone": name,
                    "assessment": f"Complete week {week_num} quiz or project"
                })
        
        return milestones
    
    def _get_study_tips(self, learning_style: str) -> List[str]:
        """Get study tips based on learning style."""
        base_tips = [
            "Take regular breaks (Pomodoro technique: 25 min work, 5 min break)",
            "Review material within 24 hours to improve retention",
            "Practice active recall instead of passive reading",
            "Join study groups or online communities"
        ]
        
        style_specific = {
            "visual": ["Use mind maps and diagrams", "Watch educational videos", "Create flashcards with images"],
            "auditory": ["Record and listen to lectures", "Discuss topics with others", "Use mnemonic devices"],
            "reading": ["Take detailed notes", "Summarize chapters in your own words", "Create study guides"],
            "kinesthetic": ["Practice hands-on activities", "Build projects", "Use physical manipulatives"],
            "mixed": ["Combine multiple learning methods", "Experiment with different techniques", "Adapt based on topic"]
        }
        
        return base_tips + style_specific.get(learning_style, style_specific["mixed"])
    
    def generate_progress_report(self, completed_weeks: int, total_weeks: int, 
                                 completed_hours: int, total_hours: int) -> Dict:
        """Generate a progress report for a study plan."""
        progress_percentage = (completed_weeks / total_weeks) * 100
        hours_percentage = (completed_hours / total_hours) * 100
        
        on_track = abs(progress_percentage - hours_percentage) < 20
        
        return {
            "completed_weeks": completed_weeks,
            "total_weeks": total_weeks,
            "progress_percentage": round(progress_percentage, 1),
            "completed_hours": completed_hours,
            "total_hours": total_hours,
            "hours_percentage": round(hours_percentage, 1),
            "on_track": on_track,
            "status": "On Track" if on_track else "Needs Adjustment",
            "recommendation": "Great progress! Keep it up!" if on_track else 
                            "Consider adjusting your study schedule to stay on track."
        }

study_planner_tool = StudyPlannerTool()
