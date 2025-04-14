"""
Roman Senate AI Game
Logging Utilities Module

This module provides logging functionality for both API and general game operations.
"""
import os
import time
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler
import asyncio
from colorama import init, Fore, Style
from rich.logging import RichHandler

from config import (
    LOG_DIR,
    LOG_FILE,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOG_CONSOLE_OUTPUT,
    LOG_LEVEL,
    DEBUG_LOGGING_ENABLED
)

# Initialize colorama for cross-platform color support
init()

def setup_logging():
    """Set up both general and API logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # File handler for debug logs
    file_handler = logging.FileHandler("logs/game.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Get root logger and add file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

class APILogger:
    """Handles debug logging for OpenAI API interactions."""
    
    def __init__(self,
                 log_dir: str = LOG_DIR,
                 log_file: str = LOG_FILE,
                 console_output: bool = LOG_CONSOLE_OUTPUT,
                 log_level: int = LOG_LEVEL):
        self.start_time = None
        self.total_tokens = 0
        self.last_progress_time = 0
        self.progress_update_interval = 0.5  # seconds
        
        self.logger = logging.getLogger('openai_api')
        self.logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(log_level)
        
        # Create console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            self.logger.addHandler(console_handler)
        
        # Create formatter and add it to handlers
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    async def _print_async(self, message: str) -> None:
        """Print message asynchronously to avoid blocking."""
        await asyncio.get_event_loop().run_in_executor(None, print, message)
    
    def start_api_call(self, prompt: str, params: Dict[str, Any], senator_name: str = "Unknown") -> None:
        """Log the start of an API call."""
        self.start_time = time.time()
        self.total_tokens = 0
        
        # File logging
        self.logger.debug("API Call Start: %s", datetime.now().isoformat())
        self.logger.debug("Prompt: %s", prompt)
        self.logger.debug("Parameters: %s", json.dumps(params, indent=2))
        
        # Console output
        print(f"\n{Fore.BLUE}[API Call]{Style.RESET_ALL} Generating speech for Senator {senator_name}...")
        print(f"{Fore.CYAN}[Prompt]{Style.RESET_ALL} {prompt[:50]}... (total tokens: {len(prompt.split())})")
    
    def log_token_count(self, count: int) -> None:
        """Log token count information."""
        self.total_tokens = count
        self.logger.debug("Token Count: %d", count)
    
    def log_streaming_progress(self, chunk_size: int, total_received: int) -> None:
        """Log streaming progress information."""
        current_time = time.time()
        
        # Handle case where start_time might be None
        if self.start_time is None:
            self.start_time = current_time  # Initialize it now
            
        elapsed = current_time - self.start_time
        
        # Only update progress at specified intervals
        if current_time - self.last_progress_time >= self.progress_update_interval:
            self.last_progress_time = current_time
            
            # Calculate metrics
            tokens_per_second = total_received / elapsed if elapsed > 0 else 0
            progress_color = Fore.GREEN if tokens_per_second > 10 else Fore.YELLOW
            
            # Console output
            print(f"{Fore.BLUE}[Progress]{Style.RESET_ALL} Received {total_received} tokens in {elapsed:.1f}s "
                  f"({progress_color}{tokens_per_second:.1f} tokens/s{Style.RESET_ALL})")
            
            # File logging
            self.logger.debug("Streaming Progress - Chunk Size: %d, Total Received: %d",
                            chunk_size, total_received)
    
    def log_response(self, response: str) -> None:
        """Log API response."""
        # Handle case where start_time might be None
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            
            # File logging
            self.logger.debug("Response: %s", response)
            
            # Console output
            print(f"{Fore.GREEN}[Response]{Style.RESET_ALL} First chunk received in {elapsed:.1f}s")
        else:
            # Just log the response without timing information
            self.logger.debug("Response: %s", response)
            print(f"{Fore.GREEN}[Response]{Style.RESET_ALL} Response received")
    
    def end_api_call(self) -> float:
        """Log the end of an API call and return duration."""
        end_time = time.time()
        
        # Handle case where start_time might be None
        if self.start_time is not None:
            duration = end_time - self.start_time
            
            # File logging
            self.logger.debug("API Call End: %s", datetime.now().isoformat())
            self.logger.debug("Total Time: %.2f seconds", duration)
            
            # Console output
            print(f"{Fore.GREEN}[Complete]{Style.RESET_ALL} Total time: {duration:.1f}s, "
                  f"Total tokens: {self.total_tokens}")
        else:
            duration = 0.0
            self.logger.debug("API Call End: %s (no start time recorded)", datetime.now().isoformat())
            print(f"{Fore.GREEN}[Complete]{Style.RESET_ALL} Total tokens: {self.total_tokens}")
        
        return duration


def get_logger():
    """Returns a simple logger instance."""
    if DEBUG_LOGGING_ENABLED:
        return APILogger()
    else:
        # Return a dummy logger that does nothing
        return DummyLogger()


class DummyLogger:
    """A dummy logger that does nothing - used when debug logging is disabled."""
    
    def __init__(self):
        pass
        
    def start_api_call(self, *args, **kwargs):
        pass
        
    def log_token_count(self, *args, **kwargs):
        pass
        
    def log_streaming_progress(self, *args, **kwargs):
        pass
        
    def log_response(self, *args, **kwargs):
        pass
        
    def end_api_call(self, *args, **kwargs):
        return 0.0