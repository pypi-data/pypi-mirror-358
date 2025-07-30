from ..Handlers.BaseHandler import Handler


class FSMHandlerMixin(Handler):
    def GetPassedByType(self, obj, context, **kwargs):
        return super().GetPassedByType(obj, **kwargs) + [
            context
        ]