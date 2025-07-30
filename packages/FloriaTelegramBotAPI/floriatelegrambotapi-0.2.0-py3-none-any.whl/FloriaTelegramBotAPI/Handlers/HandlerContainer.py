import inspect
from typing import Callable, Union, Literal, Any, Type

from .BaseHandler import Handler
from ..Middleware.BaseMiddleware import BaseMiddleware
from ..Types import DefaultTypes


class HandlerContainer:
    def __init__(self):
        self._handlers: list[Handler] = []
        self._mixins: list[Type] = []
        self._middleware: BaseMiddleware = BaseMiddleware()
    
    def RegisterHandler(self, func: Callable[[], Union[Literal[False], Any]], handler: Handler, *mixins: Type, **kwargs) -> Callable[[], Union[Literal[False], Any]]:
        if not inspect.iscoroutinefunction(func):
            raise ValueError()
        
        if not issubclass(handler.__class__, Handler):
            raise ValueError()
        
        for mixin in [*self._mixins, *mixins]:
            handler.__class__ = type(mixin.__name__, (mixin, handler.__class__), {})
        
        handler._func = func
        for key, value in kwargs.items():
            handler.__setattr__(key, value)
        self._handlers.append(handler)
        
        return func
    
    async def Invoke(self, obj: DefaultTypes.UpdateObject, **kwargs) -> bool:
        for handler in self._handlers:
            if await self._middleware(handler, obj, **kwargs):
                return True
        return False
    
    async def __call__(self, obj: DefaultTypes.UpdateObject, **kwargs) -> bool:
        return await self.Invoke(obj, **kwargs)
    
    @property
    def middleware(self) -> BaseMiddleware:
        return self._middleware
    @middleware.setter
    def middleware(self, value: BaseMiddleware):
        self._middleware = value
    