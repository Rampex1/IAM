_store = {}


def put_item(key, item):
    _store[key] = item
    return {"status": "ok"}


def get_item(key):
    return _store.get(key)
