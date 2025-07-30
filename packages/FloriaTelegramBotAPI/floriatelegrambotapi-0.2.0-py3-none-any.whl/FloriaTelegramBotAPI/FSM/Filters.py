from typing import Any

from ..Filters.BaseFilter import Filter

from .FSMContext import FSMContext


class State(Filter):
    def __init__(self, state: Any):
        super().__init__()
        self._state = state
    
    def Check(self, obj, context: FSMContext, **kwargs):
        return context.state == self._state
