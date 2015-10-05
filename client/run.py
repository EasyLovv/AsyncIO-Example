import asyncio

from client import GameClient
import settings

import os
import logging
import logging.config

logging.config.dictConfig(
    getattr(settings, 'LOGGING',
            {
                'version': 1,
                'disable_existing_loggers': False
            })
)

if settings.DEBUG:
    os.environ['PYTHONASYNCIODEBUG'] = '1'

logger = logging.getLogger('Running')

if __name__ == "__main__":
    logger.info("Creating Loop")
    loop = asyncio.get_event_loop()
    client = GameClient(loop, settings.SERVER_URL)
    try:
        logger.info("Run forever loop!")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Ctrl+C was pressed. Running stop process.")
        loop.run_until_complete(client.close())
        logger.info("Close loop")
        loop.close()

