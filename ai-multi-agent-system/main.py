"""
Main Application Entry Point
AI Multi-Agent Orchestration System
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator import get_orchestrator
from utils.logger import get_logger
from config.settings import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


async def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("AI Multi-Agent Orchestration System")
    logger.info("=" * 60)
    logger.info(f"Log Level: {settings.app.log_level}")
    logger.info(f"Poll Interval: {settings.app.message_poll_interval}s")
    logger.info(f"Max Concurrent Tasks: {settings.app.max_concurrent_tasks}")
    logger.info("=" * 60)
    
    try:
        # Get orchestrator instance
        orchestrator = get_orchestrator()
        
        # Start the orchestration system
        logger.info("Starting orchestrator...")
        await orchestrator.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise
    finally:
        logger.info("Application shutdown complete")


def run():
    """Run the application"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run()
