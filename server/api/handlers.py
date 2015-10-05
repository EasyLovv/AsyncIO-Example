import asyncio
from aiohttp import web
from aiohttp_session import get_session

import logging

import settings
from helpers import json_response, create_empty_field, get_user_id
from api.actions import actions, ActionException

import json

logger = logging.getLogger('http_handlers')

field_db_key = "field:{}:list"
items_db_key = "items:{}:set"

@asyncio.coroutine
def get_state(request):
    logger.info('Incoming {} request'.format(request.path))

    session = yield from get_session(request)
    user_id = get_user_id(session)

    logger.debug('Wait for free redis connection from pool')
    with (yield from request.app.redis_pool) as redis:
        logger.debug('Redis connection waiting finished')

        logger.debug('Get field from redis')
        field = yield from redis.lrange(field_db_key.format(user_id), 0, -1, encoding='utf-8')

        if not field:
            logger.debug('User does not have a field. Creating...')
            field = create_empty_field()
            logger.debug('Write user field to Redis...')
            yield from redis.lpush(field_db_key.format(user_id), *field)

        return json_response({
            'field': field,
            'field_size': settings.FIELD_SIZE
        })

@asyncio.coroutine
def update_state(request):
    logger.info('Incoming {} request'.format(request.path))

    session = yield from get_session(request)
    user_id = get_user_id(session)

    yield from request.post()

    req_actions = request.POST.get('actions', '[]')
    req_actions = json.loads(req_actions)

    logger.debug('Wait for free redis connection from pool')
    with (yield from request.app.redis_pool) as redis:
        logger.debug('Redis connection waiting finished')
        try:
            logger.debug(
                "Requester actions is: {}".format(
                    ", ".join([req_action["type"] for req_action in req_actions])
                )
            )

            for req_action in req_actions:
                try:
                    action_cls = actions[req_action['type']]
                except KeyError:
                    msg = "Error! There is no such action type as %s" % req_action['type']
                    logger.error(msg)
                    return web.HTTPBadRequest(body=msg.encode('utf-8'))

                logger.debug('Begin "{}" action process'.format(req_action['type']))

                action = action_cls(field_db_key.format(user_id), items_db_key.format(user_id), redis)

                yield from action.make_action(**req_action['params'])

                logger.debug('End "{}" action process'.format(req_action['type']))

        except ActionException as error:
            logger.exception(error.body)
            return web.HTTPBadRequest(body=error.body.encode('utf-8'))

    return web.Response(body=b"Ok.")

