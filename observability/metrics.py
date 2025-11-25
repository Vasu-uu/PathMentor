import json
import time
from datetime import datetime
from pathlib import Path
from threading import Lock

class MetricsCollector:
    def __init__(self, metrics_file="metrics/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(exist_ok=True)
        self.lock = Lock()
        
        self.metrics = {
            "requests": {
                "total": 0,
                "by_endpoint": {}
            },
            "agents": {
                "total_executions": 0,
                "by_agent": {},
                "average_duration_ms": 0
            },
            "tools": {
                "total_calls": 0,
                "by_tool": {},
                "success_rate": 0
            },
            "sessions": {
                "total_created": 0,
                "active": 0
            },
            "execution_times": [],
            "errors": {
                "total": 0,
                "by_type": {}
            }
        }
        
        self._load_metrics()
    
    def _load_metrics(self):
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    loaded = json.load(f)
                    self.metrics.update(loaded)
            except Exception as e:
                print(f"Could not load metrics: {e}")
    
    def _save_metrics(self):
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Could not save metrics: {e}")
    
    def increment_request(self, endpoint="/"):
        with self.lock:
            self.metrics["requests"]["total"] += 1
            if endpoint not in self.metrics["requests"]["by_endpoint"]:
                self.metrics["requests"]["by_endpoint"][endpoint] = 0
            self.metrics["requests"]["by_endpoint"][endpoint] += 1
            self._save_metrics()
    
    def record_agent_execution(self, agent_name, duration_ms):
        with self.lock:
            self.metrics["agents"]["total_executions"] += 1
            
            if agent_name not in self.metrics["agents"]["by_agent"]:
                self.metrics["agents"]["by_agent"][agent_name] = {
                    "count": 0,
                    "total_duration_ms": 0
                }
            
            self.metrics["agents"]["by_agent"][agent_name]["count"] += 1
            self.metrics["agents"]["by_agent"][agent_name]["total_duration_ms"] += duration_ms
            
            total_duration = sum(
                agent["total_duration_ms"] 
                for agent in self.metrics["agents"]["by_agent"].values()
            )
            self.metrics["agents"]["average_duration_ms"] = (
                total_duration / self.metrics["agents"]["total_executions"]
            )
            
            self.metrics["execution_times"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "duration_ms": duration_ms
            })
            
            if len(self.metrics["execution_times"]) > 100:
                self.metrics["execution_times"] = self.metrics["execution_times"][-100:]
            
            self._save_metrics()
    
    def record_tool_call(self, tool_name, success=True):
        with self.lock:
            self.metrics["tools"]["total_calls"] += 1
            
            if tool_name not in self.metrics["tools"]["by_tool"]:
                self.metrics["tools"]["by_tool"][tool_name] = {
                    "calls": 0,
                    "successes": 0
                }
            
            self.metrics["tools"]["by_tool"][tool_name]["calls"] += 1
            if success:
                self.metrics["tools"]["by_tool"][tool_name]["successes"] += 1
            
            total_successes = sum(
                tool["successes"] 
                for tool in self.metrics["tools"]["by_tool"].values()
            )
            self.metrics["tools"]["success_rate"] = (
                total_successes / self.metrics["tools"]["total_calls"] * 100
            )
            
            self._save_metrics()
    
    def record_session_event(self, event_type):
        with self.lock:
            if event_type == "created":
                self.metrics["sessions"]["total_created"] += 1
                self.metrics["sessions"]["active"] += 1
            elif event_type == "closed":
                self.metrics["sessions"]["active"] = max(0, self.metrics["sessions"]["active"] - 1)
            
            self._save_metrics()
    
    def record_error(self, error_type):
        with self.lock:
            self.metrics["errors"]["total"] += 1
            if error_type not in self.metrics["errors"]["by_type"]:
                self.metrics["errors"]["by_type"][error_type] = 0
            self.metrics["errors"]["by_type"][error_type] += 1
            self._save_metrics()
    
    def get_metrics(self):
        with self.lock:
            return self.metrics.copy()

metrics_collector = MetricsCollector()
