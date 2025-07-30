from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional, Union

from .. import DefaultTypes
from ... import Enums


class SendMessage(BaseModel):
    chat_id: str | int
    text: str
    reply_parameters: Optional[DefaultTypes.ReplyParameters] = None
    reply_markup: Optional[Union[
        DefaultTypes.InlineKeyboardMarkup,
        DefaultTypes.ReplyKeyboardMarkup,
        DefaultTypes.ReplyKeyboardRemove,
        DefaultTypes.ForceReply
    ]] = None
    parse_mode: Optional[str] = None
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None
    entities: Optional[list[DefaultTypes.MessageEntity]] = None
    link_preview_options: Optional[DefaultTypes.LinkPreviewOptions] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None


class SendChatAction(BaseModel):
    chat_id: str | int
    action: Enums.Action
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None


class SendPhoto(BaseModel):
    chat_id: str | int
    photo: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[Enums.ParseMode] = None
    caption_entities: Optional[list[DefaultTypes.MessageEntity]] = None
    show_caption_above_media: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    reply_parameters: Optional[DefaultTypes.ReplyParameters] = None
    reply_markup: Optional[Union[
        DefaultTypes.InlineKeyboardMarkup,
        DefaultTypes.ReplyKeyboardMarkup,
        DefaultTypes.ReplyKeyboardRemove,
        DefaultTypes.ForceReply
    ]] = None
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None