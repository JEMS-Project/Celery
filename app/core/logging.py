import logging
import json
from datetime import datetime, date
from typing import Any
from functools import wraps
import traceback
import asyncio
import inspect

class JobLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_value(self, value: Any) -> str:
        """Format special types for logging"""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return str(value)

    def _sanitize_data(self, data: dict) -> dict:
        """Sanitize dictionary for logging"""
        return {
            k: self._format_value(v) 
            for k, v in data.items() 
            if not k.lower() in ['password', 'secret', 'token']
        }

    def log_error(self, error: Exception, context: dict = None):
        """Log error with full traceback and context"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': self._sanitize_data(context) if context else {}
        }
        self.logger.error(f"Error details: {json.dumps(error_details, indent=2)}")

    def log_operation(self, operation: str, data: dict = None):
        """Log operation with relevant data"""
        log_data = {
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat(),
            'data': self._sanitize_data(data) if data else {}
        }
        self.logger.info(f"Operation details: {json.dumps(log_data, indent=2)}")

def log_operation(logger: JobLogger):
    """Decorator for logging function operations"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                logger.log_operation(
                    f"Starting {func.__name__}",
                    {'args': str(args), 'kwargs': str(kwargs)}
                )
                result = await func(*args, **kwargs)
                logger.log_operation(
                    f"Completed {func.__name__}",
                    {'status': 'success'}
                )
                return result
            except Exception as e:
                logger.log_error(e, {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                logger.log_operation(
                    f"Starting {func.__name__}",
                    {'args': str(args), 'kwargs': str(kwargs)}
                )
                result = func(*args, **kwargs)
                logger.log_operation(
                    f"Completed {func.__name__}",
                    {'status': 'success'}
                )
                return result
            except Exception as e:
                logger.log_error(e, {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                raise

        # Use inspect instead of asyncio.iscoroutinefunction
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator