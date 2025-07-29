from typing import Any, Union


def setattribute(value: Union[dict, object], k: str, v: Any):
    if hasattr(value, "__setattr__"):
        value.__setattr__(k, v)
    return value
