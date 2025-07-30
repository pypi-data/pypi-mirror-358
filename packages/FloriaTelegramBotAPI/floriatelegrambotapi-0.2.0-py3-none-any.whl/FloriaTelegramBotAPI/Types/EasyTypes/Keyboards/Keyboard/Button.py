from typing import Optional, Type
from .....Types import DefaultTypes


def Button(
    text: str,
    request_contact: Optional[bool] = None,
    request_location: Optional[bool] = None,
    request_users: Optional[DefaultTypes.KeyboardButtonRequestUsers] = None,
    request_chat: Optional[DefaultTypes.KeyboardButtonRequestChat] = None,
    request_poll: Optional[DefaultTypes.KeyboardButtonPollType] = None,
    web_app: Optional[DefaultTypes.WebAppInfo] = None,
) -> DefaultTypes.KeyboardButton:
    return DefaultTypes.KeyboardButton(
        text=text,
        request_users=request_users,
        request_chat=request_chat,
        request_contact=request_contact,
        request_location=request_location,
        request_poll=request_poll,
        web_app=web_app
    )
