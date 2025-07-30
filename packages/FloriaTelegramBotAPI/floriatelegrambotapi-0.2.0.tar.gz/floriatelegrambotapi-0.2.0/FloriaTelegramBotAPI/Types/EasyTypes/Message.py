from typing import Optional, Union, Any
from pydantic import ConfigDict

from .. import DefaultTypes
from ... import Utils, Enums


class Message:
    def __init__(self, bot, message: DefaultTypes.Message):
        self.bot = bot
        self.origin = message
    
    async def Send(
        self,
        text: str,
        reply_parameters: Optional[DefaultTypes.ReplyParameters] = None,
        reply_markup: Optional[Union[
            DefaultTypes.InlineKeyboardMarkup,
            DefaultTypes.ReplyKeyboardMarkup,
            DefaultTypes.ReplyKeyboardRemove,
            DefaultTypes.ForceReply
        ]] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        entities: Optional[list[DefaultTypes.MessageEntity]] = None,
        link_preview_options: Optional[DefaultTypes.LinkPreviewOptions] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        **kwargs
    ) -> 'Message': 
        kwargs.update(Utils.RemoveKeys(locals(), 'self', 'kwargs'))
        kwargs.setdefault('chat_id', self.chat.id)
        
        return Message(self.bot, await self.bot.methods.SendMessage(**kwargs))
    
    async def Answer(
        self,
        text: str,
        reply_markup: Optional[Union[
            DefaultTypes.InlineKeyboardMarkup,
            DefaultTypes.ReplyKeyboardMarkup,
            DefaultTypes.ReplyKeyboardRemove,
            DefaultTypes.ForceReply
        ]] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        entities: Optional[list[DefaultTypes.MessageEntity]] = None,
        link_preview_options: Optional[DefaultTypes.LinkPreviewOptions] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        **kwargs
    ) -> 'Message':
        kwargs.update(Utils.RemoveKeys(locals(), 'self', 'kwargs'))
        kwargs.update({
            'reply_parameters': DefaultTypes.ReplyParameters(
                message_id=self.id,
                chat_id=self.chat.id
            )
        })
        
        return await self.Send(**kwargs)

    async def SendPhoto(
        self,
        photo: str | bytes,
        caption: Optional[str] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        caption_entities: Optional[list[DefaultTypes.MessageEntity]] = None,
        show_caption_above_media: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        reply_parameters: Optional[DefaultTypes.ReplyParameters] = None,
        reply_markup: Optional[Union[
            DefaultTypes.InlineKeyboardMarkup,
            DefaultTypes.ReplyKeyboardMarkup,
            DefaultTypes.ReplyKeyboardRemove,
            DefaultTypes.ForceReply
        ]] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        **kwargs
    ):
        kwargs.update(Utils.RemoveKeys(locals(), 'self', 'kwargs'))
        kwargs.setdefault('chat_id', self.chat.id)
        
        return Message(self.bot, await self.bot.methods.SendPhoto(**kwargs))
    
    @property
    def text(self):
        return self.origin.text
    
    @property
    def chat(self):
        return self.origin.chat
    
    @property
    def from_user(self):
        return self.origin.from_user
    
    @property
    def id(self):
        return self.origin.message_id
    
    
    