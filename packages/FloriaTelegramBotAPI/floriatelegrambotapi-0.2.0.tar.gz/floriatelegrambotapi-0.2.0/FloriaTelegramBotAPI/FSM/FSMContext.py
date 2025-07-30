from typing import Any, Optional


class FSMContext:
    def __init__(
        self,
        user_id: int,
        state: Any = None,
    ):
        self._user_id: int = user_id
        self._state: Optional[Any] = state
        self._data: dict[str, Optional[Any]] = {}

# data    
    def SetData(self, **kwargs):
        self._data.update(kwargs)
    
    def GetData(self) -> dict[str, Optional[Any]]:
        return self._data.copy()
    
    def PopData(self) -> dict[str, Optional[Any]]:
        data = self.GetData()
        self.ClearData()
        return data
    
    def ClearData(self, default: dict[str, Optional[Any]] = None):
        self._data = default or {}
    
    @property
    def data(self) -> dict[str, Optional[Any]]:
        return self.GetData()
    
# state
    def SetState(self, value: Optional[Any]):
        self._state = value
    
    def ClearState(self):
        self._state = None
    
    def GetState(self) -> Optional[Any]:
        return self._state
    
    @property
    def state(self) -> Optional[Any]:
        return self.GetState()
    
    @state.setter
    def state(self, value: Optional[Any]):
        self.SetState(value)
    
    def Clear(self):
        self.ClearState()
        self.ClearData()
    