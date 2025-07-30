"""General utility functions for the gh-project-v2 library."""

import os
from datetime import datetime
from pathlib import Path


def log_message(message: str) -> None:
    """Log a message to a file if LOG_FILE environment variable is set.

    This function writes log messages to a file specified by the LOG_FILE
    environment variable. If the variable is not set, no logging occurs.

    The log format is: [%Y-%m-%d %H:%M:%S] <log message>
    Each log entry is separated by newlines.

    Args:
        message (str): The message to log

    Example:
        >>> import os
        >>> os.environ['LOG_FILE'] = '/tmp/test.log'
        >>> log_message("This is a test message")
        # Writes: [2024-01-01 12:00:00] This is a test message
    """
    log_file_path = os.environ.get('LOG_FILE')

    if not log_file_path:
        # No logging if LOG_FILE is not set
        return

    # Format the timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"

    try:
        # Create parent directories if they don't exist
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Append the log entry to the file
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except (OSError, IOError):
        # Silently ignore logging errors to avoid disrupting the main application
        # In a production environment, you might want to use a fallback logging mechanism
        pass
