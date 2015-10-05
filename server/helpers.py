from aiohttp import web

import json
import uuid

import settings


def json_response(data, serialize=True, **kwargs):
    kwargs.setdefault('content_type', 'application/json')
    if serialize:
        return web.Response(body=json.dumps(data).encode('utf-8'), **kwargs)
    else:
        return web.Response(body=data.encode('utf-8'), **kwargs)

create_uid = lambda: uuid.uuid4().hex

create_empty_field = lambda: ['']*(settings.FIELD_SIZE[0]*settings.FIELD_SIZE[1])

def get_user_id(session):
    try:
        user_id = session['user_id']
    except KeyError:
        user_id = create_uid()
        session['user_id'] = user_id

    return user_id

redis_indexOf = """
local items = redis.call('lrange', '%(key)s', 0, -1)
for i=1,#items do
    if items[i] == '%(val)s' then
       return i - 1
    end
end
return -1
"""