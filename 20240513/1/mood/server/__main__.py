"""Start server."""
from . import main
import asyncio


def run():
    asyncio.run(main())


run()
