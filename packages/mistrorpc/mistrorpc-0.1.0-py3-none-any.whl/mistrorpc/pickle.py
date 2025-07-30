from abc import ABC, abstractmethod
import typing
import json
import base64

_jsonable_types = typing.Union[None, int, bool, float, str, list, dict]

class AbstractPickleType(ABC):
    @abstractmethod
    def discrimination(self, object) -> bool:
        return False
    @abstractmethod
    def pickle(self, pickler, object) -> dict[str, _jsonable_types]:
        return {}
    @abstractmethod
    def unpickle(self, pickler, object: dict[str, _jsonable_types]):
        return None

class StandardValuePickler(AbstractPickleType):
    def discrimination(self, object):
        return isinstance(object, int) or isinstance(object, float) or isinstance(object, complex) or isinstance(object, str) or object is None
    def pickle(self, pickler, object):
        if isinstance(object, float):
            return {"": [object]}
        if isinstance(object, complex):
            return {"": [object.real, object.imag]}
        return {"": object}
    def unpickle(self, pickler, v):
        object = v[""]
        if isinstance(object, list):
            if len(object) == 1 and (isinstance(object[0], float) or isinstance(object[0], int)):
                return float(object[0])
            if len(object) == 2 and (isinstance(object[0], float) or isinstance(object[0], int)) and (isinstance(object[1], float) or isinstance(object[1], int)):
                return complex(float(object[0]), float(object[1]))
            raise ValueError("Unknown data")
        if isinstance(object, float):
            object = int(object)
        return object

class StandardContainerPickler(AbstractPickleType):
    def discrimination(self, object):
        return isinstance(object, list) or isinstance(object, set) or isinstance(object, tuple) or isinstance(object, dict)
    def __encode_dictkey(self, pickler, key):
        if isinstance(key, str):
            return f"s{key}"
        elif key is True:
            return "cT"
        elif key is False:
            return "cF"
        elif key is None:
            return "cN"
        elif isinstance(key, int):
            return f"i{key}"
        else:
            return "h"+json.dumps(pickler.pickle(key))
    def __decode_dictkey(self, pickler, key: str):
        if key.startswith("s"):
            return key[1:]
        elif key.startswith("i"):
            return int(key[1:])
        elif key.startswith("h"):
            return pickler.unpickle(json.loads(key[1:]))
        elif key == "cT":
            return True
        elif key == "cF":
            return False
        elif key == "cN":
            return None
        else:
            raise ValueError("Bad key")
    def __encode_value(self, pickler, value):
        if isinstance(value, int) or isinstance(value, str) or isinstance(value, float) or value is None:
            return value
        if isinstance(value, list):
            return [ self.__encode_value(pickler, n) for n in value ]
        return pickler.pickle(value)
    def __decode_value(self, pickler, value):
        if isinstance(value, int) or isinstance(value, str) or isinstance(value, float) or value is None:
            return value
        if isinstance(value, list):
            return [ self.__decode_value(pickler, n) for n in value ]
        return pickler.unpickle(value)
    def pickle(self, pickler, object):
        if isinstance(object, dict):
            return {"": { self.__encode_dictkey(pickler, k): self.__encode_value(pickler, v) for k, v in object.items() }, "t": "d"}
        if isinstance(object, list):
            return {"": [ self.__encode_value(pickler, v) for v in object ], "t": "l"}
        if isinstance(object, set):
            return {"": [ self.__encode_value(pickler, v) for v in object ], "t": "s"}
        if isinstance(object, tuple):
            return {"": [ self.__encode_value(pickler, v) for v in object ], "t": "t"}
    def unpickle(self, pickler, object):
        if object["t"] == "d":
            return { self.__decode_dictkey(pickler, k): self.__decode_value(pickler, v) for k, v in object[""].items() }
        elif object["t"] == "l":
            return list([ self.__decode_value(pickler, v) for v in object[""] ])
        elif object["t"] == "s":
            return set([ self.__decode_value(pickler, v) for v in object[""] ])
        elif object["t"] == "t":
            return tuple([ self.__decode_value(pickler, v) for v in object[""] ])

class BytecodePickler(AbstractPickleType):
    def discrimination(self, object):
        return isinstance(object, bytes)
    def pickle(self, pickler, object):
        return {"": base64.b85encode(object).decode("ascii")}
    def unpickle(self, pickler, object):
        return base64.b85decode(object[""])

class Pickler:
    def __init__(self):
        self.__picklers: dict[str, AbstractPickleType] = {
            "S": StandardValuePickler(),
            "C": StandardContainerPickler(),
            "B": BytecodePickler()
        }
    def pickle(self, object) -> dict:
        for name, pickler in self.__picklers.items():
            if pickler.discrimination(object):
                T = { f"@{k}": v for k, v in pickler.pickle(self, object).items() }
                T["T"] = name
                return T
        raise ValueError("There are not pickler for process this object!")
    def unpickle(self, object: dict[str, _jsonable_types]) -> typing.Any:
        return self.__picklers[object["T"]].unpickle(self, { k[1:]: v for k, v in object.items() if k.startswith("@") })
    def register_pickler(self, name: str, pickler: AbstractPickleType):
        self.__picklers[name.lower()] = pickler