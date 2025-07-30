'''
    Types from Telegram Bot API
'''

from .Common import *


UpdateObject = Union[
    Message,
    CallbackQuery
]