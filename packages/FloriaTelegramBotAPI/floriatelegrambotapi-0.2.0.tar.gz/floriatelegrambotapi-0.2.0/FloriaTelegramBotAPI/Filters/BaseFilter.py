from ..Types import DefaultTypes


class Filter:
    def Check(self, obj: DefaultTypes.UpdateObject, **kwargs) -> bool:
        raise NotImplementedError()
        
    def __call__(self, obj: DefaultTypes.UpdateObject, **kwargs) -> bool:
        return self.Check(obj, **kwargs)
