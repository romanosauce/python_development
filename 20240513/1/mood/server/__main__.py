"""Start server."""
from . import main
import asyncio


def run():
    """Entry point for wheel."""
    asyncio.run(main())


run()
