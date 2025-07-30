from ..Types import DefaultTypes
from .BaseFilter import Filter
from .. import Utils


class FilterContainer:
    def __init__(self, *filters: Filter):
        self._filters: list[Filter] = Utils.Validator.List(Filter, filters)
        
    def Validate(self, obj: DefaultTypes.UpdateObject, **kwargs) -> bool:
        for filter in self._filters:
            if not filter(obj, **kwargs):
                return False
        return True