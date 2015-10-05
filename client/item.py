import random
import json
import logging

logger = logging.getLogger('Field')

class Item(object):

    def __init__(self, item_id, x, y):
        self._id = item_id
        self._x = x
        self._y = y

    @classmethod
    def create_rand(cls, len_x, len_y):
        item_id = "Item_{}".format(random.randint(1, len_x*len_y))
        return cls(item_id, *cls.get_rand_position(len_x, len_y))

    @classmethod
    def get_rand_position(cls, len_x, len_y):
        return random.randint(0, len_x-1), random.randint(0, len_y-1)

    def move(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def id(self):
        return self._id


class Field(object):

    def __init__(self, json_data):
        logger.debug("Creating new Field")
        self._items = list()
        self._len_x = 0
        self._len_y = 0
        self.fill_field(json_data)

    def fill_field(self, json_str):
        if self._items:
            self._items = list()

        json_obj = json.loads(json_str)
        self._len_x, self._len_y = json_obj['field_size']
        logger.debug("Fill Field {0}:{1}".format(self._len_x, self._len_y))
        raw_field = json_obj['field']

        for x in range(self._len_x):
            for y in range(self._len_y):
                raw_item_id = raw_field[x+y]
                if raw_item_id:
                    item = Item(raw_item_id, x, y)
                    self._items.append(item)

        logger.debug("You have {} items".format(len(self._items)))

    def __len__(self):
        return len(self._items)

    def rand_item_add(self):
        item = Item.create_rand(self._len_x, self._len_y)
        self._items.append(item)
        logger.debug("Create random item id:{0} x:{1} y:{2}".format(item.id, item.x, item.y))
        return item

    def rand_item_move(self):
        item = random.choice(self._items)
        item.move(*Item.get_rand_position(self._len_x, self._len_y))
        logger.debug("Move item id:{0} to x:{1} y:{2}".format(item.id, item.x, item.y))
        return item

    def rand_item_remove(self):
        item = random.choice(self._items)
        self._items.remove(item)
        logger.debug("Remove item id:{0}".format(item.id))
        return item



