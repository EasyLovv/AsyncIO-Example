from api.handlers import get_state, update_state

routes = (
    ('GET', '/getState', get_state),
    ('POST', '/updateState', update_state),
)