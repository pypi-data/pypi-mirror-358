from typing import Union, Optional, Any, Callable, Type, Literal, get_args, get_origin
from pydantic import BaseModel
import inspect
import os

from .Types import DefaultTypes


def RemoveKeys(data: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {
        key: value 
        for key, value in data.items()
        if key not in keys
    }

def RemoveValues(data: dict[str, Any], *values: Any) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value not in values
    }

def ToDict(**kwargs: Any) -> dict[str, Any]:
    return kwargs

def ConvertToJson(
    obj: Union[
        dict[str, Any],
        list[Any],
        Any
    ]
) -> Union[
    dict[str, Any],
    list[Any],
    Any
]:
    if isinstance(obj, dict):
        return {
            key: ConvertToJson(value)
            for key, value in obj.items()
        }
    
    elif isinstance(obj, list | tuple):
        return [
            ConvertToJson(value) 
            for value in obj
        ]
    
    elif issubclass(obj.__class__, BaseModel):
        obj: BaseModel = obj
        return obj.model_dump(mode='json', exclude_none=True)
    
    elif obj.__class__ in [str, int, float, bool] or obj in [None]:
        return obj
    
    raise RuntimeError('Unsupport type')

def GetPathToObject(obj: Any):
    return f'File "{os.path.abspath(inspect.getfile(obj))}", line {inspect.getsourcelines(obj)[1]}'

class LazyObject:
    def __init__(self, returning_type: Type, func: Callable[[], Any], *args, **kwargs):
        self.type = returning_type
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self):
        return self.func(*self.args, **self.kwargs)

async def InvokeFunction(
    func: Callable, 
    *,
    passed_by_name: dict[str, Any] = {}, 
    passed_by_type: list[Any] = {}
):
    passed_by_type_dict = {}
    for value in passed_by_type:
        if value is None:
            continue
        if issubclass(value.__class__, LazyObject):
            passed_by_type_dict[value.type] = value
        else:
            passed_by_type_dict[value.__class__] = value
        
    kwargs: dict[str, Any] = {}
    for key, type in func.__annotations__.items():
        if key in passed_by_name:
            kwargs[key] = passed_by_name[key]
            continue
        
        types_to_try = None
        if get_origin(type) is Union:
            types_to_try = get_args(type)
        else:
            types_to_try = (type,)
        
        for try_type in types_to_try:
            if try_type not in passed_by_type_dict:
                continue
            value = passed_by_type_dict[try_type]
            kwargs[key] = value() if issubclass(value.__class__, LazyObject) else value
            break
        
        else:
            raise RuntimeError(f"""\n\tNo passed Name or Type found for field '{key}({type})' of function: \n\t{GetPathToObject(func)}""")
        
    return await func(**kwargs)

async def CallHandlers(
    handlers,
    *args,
    **kwargs
) -> bool:
    for handler in handlers:
        if await handler(*args, **kwargs):
            return True
    return False

class Validator:
    @staticmethod
    def List(type: Type[Any], data: list[Any], subclass: bool = True) -> list[Any]:
        for item in data:
            if subclass and not issubclass(item.__class__, type) or not subclass and not isinstance(item, type):
                raise ValueError()
        return [*data]
        
class Transformator:
    @staticmethod
    def GetUser(obj: DefaultTypes.UpdateObject) -> DefaultTypes.User:
        if isinstance(obj, DefaultTypes.Message):
            return obj.from_user
        elif isinstance(obj, DefaultTypes.CallbackQuery):
            return obj.from_user
        raise ValueError()
    
    @staticmethod
    def GetChat(obj: DefaultTypes.UpdateObject) -> DefaultTypes.Chat:
        if isinstance(obj, DefaultTypes.Message):
            return obj.chat
        elif isinstance(obj, DefaultTypes.CallbackQuery):
            return obj.message.chat
        raise ValueError()