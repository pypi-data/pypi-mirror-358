def CheckCredential(key):
    import os
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Missing required credential: {key}")
    return value
