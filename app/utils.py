def filter_dict(dictionary: dict, allowed_keys: list | tuple) -> dict:
    """
    Remove key from a dictionary if it is not in the list of allowed keys.
    """
    return {k: v for k, v in dictionary.items() if k in allowed_keys}
