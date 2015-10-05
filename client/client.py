import aiohttp

import asyncio

import logging
import json

import settings
from item import Field


class GameClient(object):

    def __init__(self, loop, url):
        self.logger = logging.getLogger('GameClient')
        self.logger.info("Create GameClient")
        self._loop = loop
        self._client = aiohttp.ClientSession()
        self.logger.debug("Server addess is {}".format(url))
        self._url = url
        self._task = loop.create_task(self.create_task())
        self._field = None
        self._actions = [getattr(self, method_name)
                         for method_name in filter(lambda x: x.startswith('action_decide'), dir(self))]

    @asyncio.coroutine
    def close(self):
        self.logger.debug("Close GameClient")
        self._client.close()
        self._task.cancel()
        self.logger.debug("Wait for task end")
        yield from asyncio.wait([self._task])

    @asyncio.coroutine
    def create_task(self):
        self.logger.info("Create main task")
        yield from self.get_state()
        try:
            while True:
                yield from self.update_state()
                yield from asyncio.sleep(settings.UPDATE_STATE_PERIOD)
        except asyncio.futures.CancelledError:
            self.logger.info('Main task was stopped')

    @asyncio.coroutine
    def get_state(self):
        self.logger.info('Call getState')

        try:
            resp = yield from self._client.get('{0}/{1}'.format(self._url, 'getState'))
        except aiohttp.errors.ClientOSError as e:
            self.logger.error(e)
            raise KeyboardInterrupt()


        data = (yield from resp.read()).decode('utf-8')

        yield from resp.release()

        if resp.status != 200:
            self.logger.exception('Status {0}:{1} retry after {2}sec'.format(resp.status,
                                                                             data,
                                                                             settings.RETRY_PERIOD))
            yield from asyncio.sleep(settings.RETRY_PERIOD)
            yield from self.get_state()
        else:
            self.logger.debug("Success!! Server return: {}".format(data))
            self._field = Field(data)

    @asyncio.coroutine
    def update_state(self):
        self.logger.info('Call updateState')

        decided_actions = self.decide_actions()

        try:
            resp = yield from self._client.post('{0}/{1}'.format(self._url, 'updateState'),
                                                data={'actions': json.dumps(decided_actions)})
        except aiohttp.errors.ClientOSError as e:
            self.logger.error(e)
            raise KeyboardInterrupt()

        data = (yield from resp.read()).decode('utf-8')
        yield from resp.release()

        if resp.status != 200:
            self.logger.exception('Status {0}:{1} retry after {2}sec'.format(resp.status,
                                                                             data,
                                                                             settings.RETRY_PERIOD))
            yield from self.get_state()

    def decide_actions(self):
        resp = []
        for action in self._actions:
            action_resp = action()
            if action_resp is not None:
                resp.append(action_resp)

        return resp

    def action_decide_add_item(self):
        if len(self._field) < 20:
            item = self._field.rand_item_add()
            return {
                'type': 'addItem',
                'params': {
                    'id': item.id,
                    'x': item.x,
                    'y': item.y
                }
            }
        else:
            return None

    def action_decide_move_item(self):
        if len(self._field) >= 1:
            item = self._field.rand_item_move()
            return {
                'type': 'moveItem',
                'params': {
                    'id': item.id,
                    'x': item.x,
                    'y': item.y
                }

            }
        else:
            return None

    def action_decide_remove_item(self):
        if len(self._field) > 100:
            item = self._field.rand_item_remove()
            return {
                'type': 'moveItem',
                'params': {'id': item.id}

            }
