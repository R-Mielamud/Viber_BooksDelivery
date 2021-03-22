def deep_get(obj, prop):
    names = prop.split(".")
    value = obj

    for name in names:
        if False if type(obj) == dict else not hasattr(obj, name):
            return None

        if type(obj) == dict:
            value = obj.get(name)
        else:
            value = getattr(obj, name)

    return value
