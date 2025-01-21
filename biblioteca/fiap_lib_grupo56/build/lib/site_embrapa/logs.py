import logging
import sys
from logging.handlers import RotatingFileHandler

# Basic configuration
def setup_logging():
    # Create a root logger
    logger = logging.getLogger('my_application')
    logger.setLevel(logging.DEBUG)

    # Create formatters
    # 1. Standard format with timestamp, log level, and message
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 2. Simple format for console output
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Console Handler (writes to console/terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File Handler (writes to a log file with rotation)
    file_handler = RotatingFileHandler(
        'app.log',           # Log file name
        maxBytes=1024 * 1024,  # 1 MB per file
        backupCount=3         # Keep 3 backup files
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(standard_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Example function to demonstrate logging
def example_function(logger):
    # Different log levels
    logger.debug('This is a debug message')
    logger.info('Application is running normally')
    logger.warning('Something might be wrong')
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError:
        logger.error('Attempted to divide by zero', exc_info=True)

def main():
    # Setup logging
    logger = setup_logging()

    # Log application start
    logger.info('Application started')

    # Run example function
    example_function(logger)

    # Log application end
    logger.info('Application completed')

if __name__ == '__main__':
    main()