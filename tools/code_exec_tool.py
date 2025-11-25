import sys
import io
import traceback
from typing import Dict, Any, Optional
import re

class CodeExecutionTool:
    """
    Tool for safe execution of Python code snippets.
    Useful for calculations, data processing, and educational examples.
    """
    
    def __init__(self):
        self.name = "code_executor"
        self.description = "Safely executes Python code and returns output"
        self.max_execution_time = 5
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute Python code safely with limited scope.
        
        Args:
            code: Python code to execute
            context: Optional dictionary of variables to make available
        
        Returns:
            Dictionary containing output, errors, and execution status
        """
        
        if not self._is_safe_code(code):
            return {
                "success": False,
                "output": "",
                "error": "Code contains potentially unsafe operations",
                "code": code
            }
        
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            sys.stdout = stdout
            sys.stderr = stderr
            
            local_context = context.copy() if context else {}
            
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'True': True,
                    'False': False,
                    'None': None,
                }
            }
            
            exec(code, safe_globals, local_context)
            
            output = stdout.getvalue()
            errors = stderr.getvalue()
            
            result = {
                "success": True,
                "output": output,
                "error": errors if errors else None,
                "code": code,
                "context": {k: str(v) for k, v in local_context.items() if not k.startswith('_')}
            }
            
        except Exception as e:
            result = {
                "success": False,
                "output": stdout.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                "code": code
            }
        
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        return result
    
    def _is_safe_code(self, code: str) -> bool:
        """
        Check if code is safe to execute.
        Blocks dangerous operations.
        """
        
        dangerous_patterns = [
            r'\bimport\s+os\b',
            r'\bimport\s+sys\b',
            r'\bimport\s+subprocess\b',
            r'\b__import__\b',
            r'\beval\b',
            r'\bexec\b',
            r'\bopen\b',
            r'\bfile\b',
            r'\bcompile\b',
            r'\bglobals\b',
            r'\blocals\b',
            r'\b__\w+__\b',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False
        
        return True
    
    def execute_math(self, expression: str) -> Dict[str, Any]:
        """
        Execute a mathematical expression safely.
        
        Args:
            expression: Mathematical expression as string
        
        Returns:
            Result of the calculation
        """
        
        code = f"result = {expression}\nprint(result)"
        
        result = self.execute(code)
        
        if result["success"]:
            try:
                output = result["output"].strip()
                result["result"] = float(output) if '.' in output else int(output)
            except:
                pass
        
        return result
    
    def execute_educational_example(self, topic: str, code: str) -> Dict[str, Any]:
        """
        Execute educational code examples with context.
        
        Args:
            topic: Topic being demonstrated
            code: Example code
        
        Returns:
            Execution result with educational context
        """
        
        result = self.execute(code)
        result["topic"] = topic
        result["educational"] = True
        
        return result

code_executor_tool = CodeExecutionTool()
