"""
Application entry point.
"""

from ui_components import MainApplication
from logger import logger


def main():
    """Start the UI application and handle top-level errors."""
    try:
        logger.info("Starting Refiner application")
        app = MainApplication()
        app.run()
        logger.info("Refiner application closed")
    except Exception as e:
        logger.critical(f"Fatal error in main application: {str(e)}")
        raise


if __name__ == "__main__":
    main()
