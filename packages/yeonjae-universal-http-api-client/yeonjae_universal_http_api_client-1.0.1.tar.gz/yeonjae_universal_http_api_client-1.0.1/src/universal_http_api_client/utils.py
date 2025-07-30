"""
독립적인 유틸리티 모듈
"""
import logging
import time
from typing import Any, Dict, Optional


class ModuleIOLogger:
    """모듈 입출력 로거 - shared.utils.logging.ModuleIOLogger 대체"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = logging.getLogger(f"ModuleIO.{module_name}")
    
    def log_input(self, operation: str, **kwargs):
        """입력 로깅"""
        self.logger.debug(f"[{self.module_name}] INPUT {operation}: {kwargs}")
    
    def log_output(self, operation: str, result: Any, execution_time: Optional[float] = None):
        """출력 로깅"""
        log_msg = f"[{self.module_name}] OUTPUT {operation}: success"
        if execution_time:
            log_msg += f" (took {execution_time:.3f}s)"
        self.logger.debug(log_msg)
    
    def log_error(self, operation: str, error: Exception, execution_time: Optional[float] = None):
        """에러 로깅"""
        log_msg = f"[{self.module_name}] ERROR {operation}: {type(error).__name__}: {error}"
        if execution_time:
            log_msg += f" (took {execution_time:.3f}s)"
        self.logger.error(log_msg)


def setup_logging(level: str = "INFO") -> None:
    """로깅 설정"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
