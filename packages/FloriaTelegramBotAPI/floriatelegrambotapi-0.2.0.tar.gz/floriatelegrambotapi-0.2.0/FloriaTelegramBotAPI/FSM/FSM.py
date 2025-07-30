from typing import Any

from ..Router import Router
from .. import Utils

from .FSMContext import FSMContext
from .FSMHandlerMixin import FSMHandlerMixin

class FSM(Router):
    def __init__(self, *filters):
        super().__init__(*filters)
        self._handlers._mixins = [FSMHandlerMixin]
        
        self._users: dict[int, Any] = {}
    
    def Processing(self, obj, **kwargs):
        user = Utils.Transformator.GetUser(obj)
        context = self.GetOrCreateContext(user.id)
        
        return super().Processing(obj, context=context, **kwargs)
    
    def GetOrCreateContext(self, user_id: int):
        context = self._users.get(user_id)
        if context is None:
            context = FSMContext(user_id)
            self._users[user_id] = context
        return context
    