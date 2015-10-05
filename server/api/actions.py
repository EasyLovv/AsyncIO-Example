import abc
import asyncio

import logging

import settings
from helpers import redis_indexOf

logger = logging.getLogger('actions')

class AbstractAction(metaclass=abc.ABCMeta):

    def __init__(self, field_db_key, items_db_key, redis):
        self._redis = redis
        self._field_db_key = field_db_key
        self._items_db_key = items_db_key

    @abc.abstractclassmethod
    def get_type(cls):
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def make_action(self, *args, **kwargs):
        pass


class ActionException(Exception):
    # Base class for all exception in action

    @property
    def body(self):
        return self.__str__()


class ExistException(ActionException):

    def __init__(self, item_id):
        self._item_id = item_id
        super().__init__()

    def __str__(self):
        return "Exception!! Item_id \"{}\" is already exists".format(self._item_id)


class NotExistException(ActionException):

    def __init__(self, item_id):
        self._item_id = item_id
        super().__init__()

    def __str__(self):
        return "Exception!! There is no item with id {}".format(self._item_id)


class NotEmptyException(ActionException):

    def __init__(self, x, y):
        self._x = x
        self._y = y
        super().__init__()

    def __str__(self):
        return "Exception!! Cell in position x:{0} y:{1} is not empty".format(self._x, self._y)


class ActionAddItem(AbstractAction):

    @classmethod
    def get_type(cls):
        return 'addItem'

    @asyncio.coroutine
    def make_action(self, *args, **kwargs):

        index = kwargs['x']+(kwargs['y']*settings.FIELD_SIZE[0])-1

        logger.debug("Creating redis transaction to get values")
        tr = self._redis.multi_exec()
        tr.sismember(self._items_db_key, kwargs['id'])
        tr.lindex(self._field_db_key, index)

        logger.debug("Executing redis transaction")
        exists, member = yield from tr.execute()

        logger.debug("Check conditions")
        if exists:
            raise ExistException(kwargs['id'])
        if member:
            raise NotEmptyException(kwargs['x'], kwargs['y'])

        logger.debug("Creating redis transaction to set values")
        tr = self._redis.multi_exec()
        tr.lset(self._field_db_key, index, kwargs['id'])
        tr.sadd(self._items_db_key, kwargs['id'])

        logger.debug("Executing redis transaction")
        yield from tr.execute()


class ActionMoveItem(AbstractAction):

    @classmethod
    def get_type(cls):
        return 'moveItem'

    @asyncio.coroutine
    def make_action(self, *args, **kwargs):
        index = kwargs['x']+(kwargs['y']*settings.FIELD_SIZE[0])-1

        logger.debug("Creating redis transaction to get values")
        tr = self._redis.multi_exec()
        tr.sismember(self._items_db_key, kwargs['id'])
        tr.lindex(self._field_db_key, index)

        logger.debug("Executing redis transaction")
        exists, member = yield from tr.execute()

        logger.debug("Check conditions")
        if not exists:
            raise NotExistException(kwargs['id'])
        if member:
            raise NotEmptyException(kwargs['x'], kwargs['y'])

        logger.debug("Creating redis transaction to get values")
        tr = self._redis.multi_exec()
        tr.eval(redis_indexOf % {"key": self._field_db_key, "val": kwargs['id']})
        tr.lset(self._field_db_key, index, kwargs['id'])

        logger.debug("Executing redis transaction")
        old_index, setter = yield from tr.execute()

        logger.debug("Remove old cell")
        self._redis.lset(self._field_db_key, old_index, '')


class ActionRemoveItem(AbstractAction):

    @classmethod
    def get_type(cls):
        return 'removeItem'

    @asyncio.coroutine
    def make_action(self, *args, **kwargs):

        logger.debug("Get cell index")
        index = yield from self._redis.eval(redis_indexOf % {"key": self._field_db_key, "val": kwargs['id']})
        if not index:
            raise NotExistException(kwargs['id'])

        logger.debug("Remove cell")
        yield from self._redis.lset(self._field_db_key, index, '')


actions = {
    cls.get_type(): cls for cls in AbstractAction.__subclasses__()
}

