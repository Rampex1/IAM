_store = {}


def put_object(key, content):
    _store[key] = content
    return {"status": "ok"}


def get_object(key):
    return _store.get(key)


def delete_object(key):
    _store.pop(key, None)
