def plugin_version(version: str):
    def decorator(func):
        func.hookline_version = version
        return func

    return decorator
