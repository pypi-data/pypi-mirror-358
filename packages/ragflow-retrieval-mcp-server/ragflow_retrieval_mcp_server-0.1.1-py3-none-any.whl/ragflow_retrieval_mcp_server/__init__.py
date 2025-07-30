import asyncio
from . import server


def main_sse():
    """Main entry point for the package."""
    server.main_sse()

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())