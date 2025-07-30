import requests
import aiohttp
from fastapi import FastAPI
from mistrorpc.pickle import Pickler
from mistrorpc.decorator import Decorators
import pydantic

default_pickler = Pickler()

class MistroRequests(pydantic.BaseModel):
    args: list[dict]
    kwargs: dict[str, dict]

class RemoteException:
    pass

class MistroServer:
    def __init__(self, fastapi: FastAPI, password: str, pickler: Pickler = default_pickler):
        self.__fastapi = fastapi
        self.__password = password
        self.__pickler = pickler
        self.__registered = set()
    def rpc_fn(self, name: str, run_in_executor: bool=False):
        def __decorator(fn):
            if name in self.__registered:
                raise IndexError("Name are already registered")
            if run_in_executor:
                func = Decorators.run_in_executor(fn)
            else:
                func = Decorators.asynclize(fn)
            self.rpc_asyncfn(name)(func)
            return fn
        return __decorator
    def rpc_asyncfn(self, name: str):
        def __decorator(fn):
            if name in self.__registered:
                raise IndexError("Name are already registered")
            self.__registered.add(name)
            async def __real_proc(param: MistroRequests, password: str):
                if password != self.__password:
                    return {"state": "fail", "msg": "Remote Password Error!"}
                try:
                    args = [ self.__pickler.unpickle(n) for n in param.args ]
                    kwargs = { k: self.__pickler.unpickle(v) for k, v in param.kwargs.items() }
                    result = await fn(*args, **kwargs)
                    return {"state": "ok", "result": self.__pickler.pickle(result)}
                except Exception as e:
                    return {"state": "fail", "msg": "PyError: "+e.__repr__()}
            self.__fastapi.post(f"/.mistro-fn/{name}")(__real_proc)
            return fn
        return __decorator

class MistroClient:
    def __init__(self, api: str, password: str, pickler: Pickler = default_pickler):
        if api.endswith("/"):
            api = api[:-1]
        self.__api = api
        self.__password = password
        self.__pickler = pickler
    def get_fn(self, name: str):
        def __dummy(*args, **kwargs):
            result = requests.post(
                url=f"{self.__api}/.mistro-fn/{name}?password={self.__password}",
                json={
                    "args": [ self.__pickler.pickle(n) for n in args ],
                    "kwargs": { k: self.__pickler.pickle(v) for k, v in kwargs }
                }
            )
            J = result.json()
            if "detail" in J:
                raise RemoteException("FastAPI: "+J["detail"].__repr__())
            elif J["state"] == "ok":
                return self.__pickler.unpickle(J["result"])
            elif J["state"] == "fail":
                raise RemoteException(J["msg"])
            else:
                raise RemoteException("unparsable responses")
        return __dummy
    def get_asyncfn(self, name: str):
        async def __dummy(*args, **kwargs):
            async with aiohttp.ClientSession() as session:
                result = await session.post(
                    url=f"{self.__api}/.mistro-fn/{name}?password={self.__password}",
                    json={
                        "args": [ self.__pickler.pickle(n) for n in args ],
                        "kwargs": { k: self.__pickler.pickle(v) for k, v in kwargs }
                    }
                )
                J = await result.json()
            if "detail" in J:
                raise RemoteException("FastAPI: "+J["detail"].__repr__())
            elif J["state"] == "ok":
                return self.__pickler.unpickle(J["result"])
            elif J["state"] == "fail":
                raise RemoteException(J["msg"])
            else:
                raise RemoteException("unparsable responses")
        return __dummy