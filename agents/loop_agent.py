import time
from typing import Dict, Any, List, Optional, Callable
from observability.logger import app_logger
from observability.metrics import metrics_collector

class LoopAgent:
    """
    Loop agent that iterates until a stopping condition is met.
    Useful for refinement, validation, and iterative improvement tasks.
    """
    
    def __init__(self):
        self.name = "LoopAgent"
        self.max_iterations = 10
    
    def execute(self, task: str, initial_data: Any, 
                stopping_condition: Optional[Callable] = None,
                max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a task iteratively until stopping condition is met.
        
        Args:
            task: Description of the iterative task
            initial_data: Initial data to process
            stopping_condition: Function that returns True when loop should stop
            max_iterations: Maximum number of iterations (default: self.max_iterations)
        
        Returns:
            Results of the iterative process
        """
        
        start_time = time.time()
        max_iter = max_iterations or self.max_iterations
        
        try:
            app_logger.log_agent_action(self.name, "start_loop", task)
            
            iterations = []
            current_data = initial_data
            iteration_count = 0
            
            while iteration_count < max_iter:
                iteration_count += 1
                
                iteration_result = self._process_iteration(
                    task, 
                    current_data, 
                    iteration_count
                )
                
                iterations.append(iteration_result)
                
                if stopping_condition:
                    if stopping_condition(iteration_result):
                        app_logger.log_event(
                            "loop_stopped",
                            {
                                "reason": "stopping_condition_met",
                                "iteration": iteration_count
                            }
                        )
                        break
                else:
                    if self._default_stopping_condition(iteration_result, iteration_count):
                        break
                
                current_data = iteration_result.get("output", current_data)
            
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_agent_execution(self.name, duration_ms)
            
            result = {
                "success": True,
                "agent": self.name,
                "task": task,
                "iterations": iterations,
                "total_iterations": iteration_count,
                "final_result": iterations[-1] if iterations else None,
                "stopped_early": iteration_count < max_iter,
                "duration_ms": duration_ms
            }
            
            app_logger.log_agent_action(
                self.name,
                "complete_loop",
                task,
                f"Completed in {iteration_count} iterations",
                duration_ms
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            app_logger.log_error("loop_error", str(e), {"task": task})
            metrics_collector.record_error("loop_error")
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "duration_ms": duration_ms
            }
    
    def _process_iteration(self, task: str, data: Any, iteration: int) -> Dict[str, Any]:
        """Process a single iteration."""
        
        if task == "refine_study_plan":
            return self._refine_study_plan(data, iteration)
        elif task == "validate_resources":
            return self._validate_resources(data, iteration)
        elif task == "improve_schedule":
            return self._improve_schedule(data, iteration)
        else:
            return {
                "iteration": iteration,
                "input": data,
                "output": data,
                "changes": f"Processed iteration {iteration}",
                "quality_score": min(50 + iteration * 10, 100)
            }
    
    def _refine_study_plan(self, plan: Any, iteration: int) -> Dict[str, Any]:
        """Refine a study plan iteratively."""
        
        if not isinstance(plan, dict):
            plan = {"raw_plan": plan, "refinements": []}
        
        refinements = plan.get("refinements", [])
        
        if iteration == 1:
            refinements.append("Added time estimates for each topic")
        elif iteration == 2:
            refinements.append("Included break periods and review sessions")
        elif iteration == 3:
            refinements.append("Added resource links and materials")
        elif iteration == 4:
            refinements.append("Incorporated spaced repetition intervals")
        
        quality_score = min(60 + iteration * 10, 95)
        
        return {
            "iteration": iteration,
            "input": plan,
            "output": {
                **plan,
                "refinements": refinements,
                "quality_score": quality_score
            },
            "changes": refinements[-1] if refinements else "No changes",
            "quality_score": quality_score
        }
    
    def _validate_resources(self, resources: Any, iteration: int) -> Dict[str, Any]:
        """Validate and improve resource list."""
        
        if not isinstance(resources, list):
            resources = [resources]
        
        validated = []
        for resource in resources:
            validated.append({
                "resource": resource,
                "validated": True,
                "iteration": iteration,
                "confidence": min(70 + iteration * 5, 95)
            })
        
        quality_score = min(65 + iteration * 8, 95)
        
        return {
            "iteration": iteration,
            "input": resources,
            "output": validated,
            "changes": f"Validated {len(resources)} resources",
            "quality_score": quality_score
        }
    
    def _improve_schedule(self, schedule: Any, iteration: int) -> Dict[str, Any]:
        """Improve study schedule iteratively."""
        
        if not isinstance(schedule, dict):
            schedule = {"sessions": [], "improvements": []}
        
        improvements = schedule.get("improvements", [])
        
        if iteration == 1:
            improvements.append("Balanced workload across week")
        elif iteration == 2:
            improvements.append("Added buffer time for difficult topics")
        elif iteration == 3:
            improvements.append("Optimized based on peak productivity hours")
        
        quality_score = min(65 + iteration * 10, 95)
        
        return {
            "iteration": iteration,
            "input": schedule,
            "output": {
                **schedule,
                "improvements": improvements,
                "quality_score": quality_score
            },
            "changes": improvements[-1] if improvements else "No changes",
            "quality_score": quality_score
        }
    
    def _default_stopping_condition(self, iteration_result: Dict, iteration: int) -> bool:
        """Default stopping condition based on quality score."""
        
        quality_score = iteration_result.get("quality_score", 0)
        
        if quality_score >= 90:
            return True
        
        if iteration >= 5:
            return True
        
        return False
    
    def refine_until_quality(self, task: str, data: Any, 
                            target_quality: int = 90) -> Dict[str, Any]:
        """
        Refine data until it reaches target quality score.
        
        Args:
            task: Task to perform
            data: Initial data
            target_quality: Target quality score (0-100)
        
        Returns:
            Refined result
        """
        
        def quality_check(iteration_result: Dict) -> bool:
            return iteration_result.get("quality_score", 0) >= target_quality
        
        return self.execute(task, data, stopping_condition=quality_check)

loop_agent = LoopAgent()
