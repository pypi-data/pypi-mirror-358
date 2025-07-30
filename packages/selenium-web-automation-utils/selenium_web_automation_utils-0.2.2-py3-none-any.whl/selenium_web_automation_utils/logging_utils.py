import logging

# Configure logging
logger = logging.getLogger("selenium_web_automation")
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Default level (users can override)
)

# Try importing colorfulPyPrint for optional color support
try:
    from colorfulPyPrint.py_color import print_error as color_error, print_done as color_done


    def print_error(msg):
        color_error(msg)
        logger.error(msg)


    def print_done(msg):
        color_done(msg)
        logger.info(msg)

except ImportError:
    def print_error(msg):
        logger.error(msg)


    def print_done(msg):
        logger.info(msg)

