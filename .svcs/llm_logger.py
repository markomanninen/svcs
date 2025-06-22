import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class LLMLogger:
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            # Find the current git project root and use its .svcs/logs directory
            log_dir = self._find_project_svcs_logs()
        self.log_dir = Path(log_dir)
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Safely ensure the log directory exists."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # If we can't create the directory (read-only filesystem, permissions, etc.)
            # fall back to a temp directory or disable logging
            import tempfile
            fallback_dir = Path(tempfile.gettempdir()) / "svcs_logs"
            fallback_dir.mkdir(exist_ok=True)
            self.log_dir = fallback_dir
            print(f"Warning: Could not create SVCS logs in {self.log_dir}, using fallback: {fallback_dir}", file=sys.stderr)
    
    def _find_project_svcs_logs(self):
        """Find the .svcs/logs directory for the current git project."""
        try:
            # Get the git root directory
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            git_root = Path(result.stdout.strip())
            return git_root / ".svcs" / "logs"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: try global SVCS directory if available
            global_svcs = Path.home() / ".svcs" / "logs"
            if global_svcs.parent.exists():
                return global_svcs
            # Last resort: temp directory
            import tempfile
            return Path(tempfile.gettempdir()) / "svcs_logs"
    
    def log_inference(self, component: str, prompt: str, response: str, model: str = "gemini", metadata: dict = None):
        """Log LLM inference with structured data for audit purposes."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "component": component,
            "model": model,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        
        # Create daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{component}_{date_str}.jsonl"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_error(self, component: str, prompt: str, error: str, model: str = "gemini", metadata: dict = None):
        """Log LLM inference errors."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "component": component,
            "model": model,
            "prompt": prompt,
            "error": error,
            "metadata": metadata or {}
        }
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        error_file = self.log_dir / f"{component}_errors_{date_str}.jsonl"
        
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# Global logger instance - lazy initialization to avoid startup issues
_logger_instance = None

def get_llm_logger():
    """Get or create the global LLM logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LLMLogger()
    return _logger_instance

# Create a proxy object that defers initialization
class LazyLLMLogger:
    def __getattr__(self, name):
        return getattr(get_llm_logger(), name)

# For backward compatibility
llm_logger = LazyLLMLogger()
