import sys
import asyncio
from pubstomp.core import main

def cli():
    asyncio.run(main())

if __name__ == "__main__":
    cli()