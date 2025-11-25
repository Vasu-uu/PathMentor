import logging
import json
from datetime import datetime
from pathlib import Path

class StructuredLogger:
    def __init__(self, name="AgentSystem", log_dir="logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            log_file = self.log_dir / f"{name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_event(self, event_type, details, level="info"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        message = json.dumps(log_entry)
        
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)
    
    def log_agent_action(self, agent_name, action, input_data, output_data=None, duration=None):
        self.log_event(
            "agent_action",
            {
                "agent": agent_name,
                "action": action,
                "input": str(input_data)[:200],
                "output": str(output_data)[:200] if output_data else None,
                "duration_ms": duration
            }
        )
    
    def log_tool_call(self, tool_name, input_data, output_data=None, success=True):
        self.log_event(
            "tool_call",
            {
                "tool": tool_name,
                "input": str(input_data)[:200],
                "output": str(output_data)[:200] if output_data else None,
                "success": success
            }
        )
    
    def log_session_event(self, session_id, event, details):
        self.log_event(
            "session_event",
            {
                "session_id": session_id,
                "event": event,
                "details": details
            }
        )
    
    def log_error(self, error_type, error_message, context=None):
        self.log_event(
            "error",
            {
                "error_type": error_type,
                "message": error_message,
                "context": context
            },
            level="error"
        )

app_logger = StructuredLogger()
