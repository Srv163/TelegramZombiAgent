import asyncio, logging, uvloop
from .config import settings
from .listener import poll_sources
from .scheduler import setup_scheduler

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')

def main():
    uvloop.install()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler = setup_scheduler()
    loop.create_task(poll_sources())
    try:
        loop.run_forever()
    finally:
        loop.stop()

if __name__ == "__main__":
    main()