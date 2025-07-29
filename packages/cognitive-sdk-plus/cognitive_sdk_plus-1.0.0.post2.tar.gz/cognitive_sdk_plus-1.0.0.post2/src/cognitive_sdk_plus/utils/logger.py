import sys
from loguru import logger
import os

class LoggerManager:
    def __init__(self):
        self.logger = logger
        # Don't configure in __init__, wait for explicit configuration
        self.log_levels_set = set()
        self.subscribers_log_enabled = False # Flag to enable subscriber logs (default: disabled)

    def set_subscriber_log_enabled(self, enable: bool):
        """Sets the status for enabling subscriber logs."""
        self.subscribers_log_enabled = enable
        # Filters check this dynamically, so no reconfiguration needed here.
        # Log only if enabling, to avoid noise when default (disabled) is used.
        if enable:
            self.logger.info("Subscriber logs enabled.")

    def configure_logger(self, log_levels=None, log_file=None):
        # Remove all existing handlers
        self.logger.remove()

        if log_levels is None:
            log_levels = 'INFO,ERROR,DEBUG'.split(',')
        elif isinstance(log_levels, str):
            log_levels = [level.strip() for level in log_levels.split(',')]  # Strip whitespace

        self.log_levels_set = set(log_levels)

        # --- Default Filter (excludes orcustrator and local data cache) ---
        def default_log_filter(record):
            # Check level AND check that the name doesn't contain the specific module paths
            is_correct_level = record["level"].name in self.log_levels_set
            is_not_orcustrator = "core_zeromq.orcustrator" not in record["name"]
            # Generalize exclusion for all subscribers
            is_not_subscriber = not record["name"].startswith("subscriber.") 
            is_not_publisher = "core_zeromq.publisher" not in record["name"]
            return is_correct_level and is_not_orcustrator and is_not_subscriber and is_not_publisher

        def log_filter(record):
            return record["level"].name in self.log_levels_set
        # --- Orcustrator Specific Filter ---
        def orcustrator_log_filter(record):
            # Check level AND check that the name DOES contain the orcustrator module path
            is_correct_level = record["level"].name in self.log_levels_set
            is_orcustrator = "core_zeromq.orcustrator" in record["name"]
            return is_correct_level and is_orcustrator
        
        # --- Subscriber Log Filter (Generic) ---
        def subscriber_log_filter(record):
            # Only allow subscriber logs if the flag is explicitly enabled
            if not self.subscribers_log_enabled:
                return False
            # Check level AND check that the name starts with "subscriber."
            is_correct_level = record["level"].name in self.log_levels_set
            is_subscriber = record["name"].startswith("subscriber.")
            return is_correct_level and is_subscriber
        
        # --- Publisher Log Filter ---
        def publisher_log_filter(record):
            # Check level AND check that the name matches the expected module path
            is_correct_level = record["level"].name in self.log_levels_set
            # Use "in" for consistency and partial path matching
            is_publisher = "core_zeromq.publisher" in record["name"]
            return is_correct_level and is_publisher

        # --- Default Log Format ---
        default_log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # --- Orcustrator Log Format (Purple) ---
        primary_orcustrator, secondary_orcustrator = "#8E44AD", "#D1C4E9"
        orcustrator_log_format = (
            f"<fg {primary_orcustrator}>" + "{time:YYYY-MM-DD HH:mm:ss.SSS}" + f"</fg {primary_orcustrator}> | "
            "<level>{level: <8}</level> | "
            f"<fg {secondary_orcustrator}>" + "{name}" + f"</fg {secondary_orcustrator}>:" + 
            f"<fg {secondary_orcustrator}>" + "{function}" + f"</fg {secondary_orcustrator}>:" + 
            f"<fg {secondary_orcustrator}>" + "{line}" + f"</fg {secondary_orcustrator}> - "
            "<level>" + f"<fg {primary_orcustrator}>" + "{message}" + f"</fg {primary_orcustrator}>" + "</level>"
        )

        # --- Subscriber Log Format (Blue Grey) ---
        primary_subscriber_color, secondary_subscriber_color = "#455A64", "#455A64"
        subscriber_log_format = (
            f"<fg {primary_subscriber_color}>" + "{time:YYYY-MM-DD HH:mm:ss.SSS}" + f"</fg {primary_subscriber_color}> | "
            "<level>{level: <8}</level> | "
            f"<fg {secondary_subscriber_color}>" + "{name}" + f"</fg {secondary_subscriber_color}>:" + 
            f"<fg {secondary_subscriber_color}>" + "{function}" + f"</fg {secondary_subscriber_color}>:" + 
            f"<fg {secondary_subscriber_color}>" + "{line}" + f"</fg {secondary_subscriber_color}> - "
            "<level>" + f"<fg {primary_subscriber_color}>" + "{message}" + f"</fg {primary_subscriber_color}>" + "</level>"
        )

        # --- Publisher Log Format (Yellow) ---
        primary_publisher, secondary_publisher = "#388E3C", "#4CAF50"
        publisher_log_format = (
            f"<fg {primary_publisher}>" + "{time:YYYY-MM-DD HH:mm:ss.SSS}" + f"</fg {primary_publisher}> | "
            "<level>{level: <8}</level> | "
            f"<fg {secondary_publisher}>" + "{name}" + f"</fg {secondary_publisher}>:" + 
            f"<fg {secondary_publisher}>" + "{function}" + f"</fg {secondary_publisher}>:" + 
            f"<fg {secondary_publisher}>" + "{line}" + f"</fg {secondary_publisher}> - "
            "<level>" + f"<fg {primary_publisher}>" + "{message}" + f"</fg {primary_publisher}>" + "</level>"
        )

        # --- Add Default Handler ---
        # Add handler for stderr (terminal) with format
        self.logger.add(
            sys.stderr,
            format=default_log_format,
            filter=default_log_filter, # Use the filter that excludes orcustrator and all subscribers
            level=0,  # Allow all levels through to our filter
            colorize=True,
            enqueue=True
        )

        # --- Add Orcustrator Specific Handler ---
        self.logger.add(
            sys.stderr, # Log to the same place
            format=orcustrator_log_format, 
            filter=orcustrator_log_filter, # Use the filter specific to orcustrator
            level=0,  # Allow all levels through to our filter
            colorize=True,
            enqueue=True
        )

        self.logger.add(
            sys.stderr, # Log to the same place
            format=subscriber_log_format, # Use generic subscriber format
            filter=subscriber_log_filter, # Use generic subscriber filter
            level=0,  # Allow all levels through to our filter
            colorize=True,
            enqueue=True
        )

        self.logger.add(
            sys.stderr, # Log to the same place
            format=publisher_log_format, 
            filter=publisher_log_filter, # Use the filter specific to orcustrator
            level=0,  # Allow all levels through to our filter
            colorize=True,
            enqueue=True
        )

        # If a log file is provided, add a file handler
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)  # Create the directory if it doesn't exist

            self.logger.add(
                log_file,
                format=default_log_format,
                filter=log_filter,
                level=0,  # Allow all levels through to our filter
                enqueue=True,
                rotation="1 day",  # Rotate logs every day (optional)
                retention="7 days",  # Keep logs for 7 days (optional)
                compression="zip"  # Compress old logs (optional)
            )

# Create a single instance of LoggerManager
logger_manager = LoggerManager()

# Export the logger instance
logger = logger_manager.logger

def configure_logger(levels, log_file=None):
    """Configure logger with specified levels and optional log file.
    
    Args:
        levels: String of comma-separated levels (e.g. "DEBUG,ERROR")
        log_file: Optional path to a log file
    """
    logger_manager.configure_logger(levels, log_file)

__all__ = ["logger", "configure_logger", "logger_manager"]
