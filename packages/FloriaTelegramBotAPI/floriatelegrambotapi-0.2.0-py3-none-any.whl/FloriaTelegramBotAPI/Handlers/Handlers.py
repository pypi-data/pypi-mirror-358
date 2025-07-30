from .BaseHandler import Handler
from ..Types import DefaultTypes, EasyTypes
from .. import Utils


class MessageHandler(Handler):
    def Validate(self, obj: DefaultTypes.UpdateObject, **kwargs):
        return isinstance(obj, DefaultTypes.Message) and super().Validate(obj, **kwargs)
    
    def GetPassedByType(self, obj: DefaultTypes.UpdateObject, bot, **kwargs):
        return super().GetPassedByType(obj, bot, **kwargs) + [
            Utils.LazyObject(EasyTypes.Message, lambda: EasyTypes.Message(bot, obj))
        ]

class CallbackHandler(Handler):
    def Validate(self, obj, **kwargs):
        return isinstance(obj, DefaultTypes.CallbackQuery) and super().Validate(obj, **kwargs)
    
    def GetPassedByType(self, obj, bot, **kwargs):
        return super().GetPassedByType(obj, bot, **kwargs) + [
            obj
        ]
