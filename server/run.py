import settings

import logging
import logging.config
import os

import asyncio
import aioredis
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

from urls import routes


logging.config.dictConfig(
    getattr(settings, 'LOGGING',
            {
                'version': 1,
                'disable_existing_loggers': False
            })
)

logger = logging.getLogger('TestServer')

if settings.DEBUG:
    os.environ['PYTHONASYNCIODEBUG'] = '1'

@asyncio.coroutine
def app_factory(loop):
    global logger

    redis_conf = getattr(settings, 'REDIS', {})

    logger.info('Create Redis connections pool')
    redis_pool = yield from aioredis.create_pool(
        (redis_conf.get('HOST', '127.0.0.1'), redis_conf.get('PORT', 6379)),
        db=redis_conf.get('DB', 0),
        password=redis_conf.get('PASSWORD', None),
        loop=loop
    )

    logger.info('Create Application object')
    app = web.Application(middlewares=[session_middleware(RedisStorage(redis_pool))])
    app.logger = logger
    app.redis_pool = redis_pool

    return app

@asyncio.coroutine
def init(loop, app, handler):

    app.logger.info('Url routes registration')
    for route in routes:
        app.router.add_route(*route)

    addr = getattr(settings, 'SERVER_LISTEN_ADDRESS', '0.0.0.0')
    port = getattr(settings, 'SERVER_LISTEN_PORT', 8080)
    app.logger.info('Starting server at {0}:{1}'.format(addr, port))
    srv = yield from loop.create_server(handler, addr, port)

    return srv

if __name__ == '__main__':
    logger.info('Create event loop')
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(app_factory(loop))
    handler = app.make_handler()
    srv = loop.run_until_complete(init(loop, app, handler))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        app.logger.info('Server was stopped')
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        app.logger.info('Clearing redis poll')
        loop.run_until_complete(app.redis_pool.clear())
        app.logger.info('Finishing application')
        loop.run_until_complete(app.finish())
    finally:
        app.logger.info('Closing loop')
        loop.close()
