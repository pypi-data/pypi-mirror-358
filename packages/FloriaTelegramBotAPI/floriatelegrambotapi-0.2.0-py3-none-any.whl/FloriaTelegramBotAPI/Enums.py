from enum import Enum


class ParseMode(Enum):
    MARKDOWNV2 = 'MarkdownV2'
    HTML = 'HTML'
    MARKDOWN = 'Markdown'

class Action(Enum):
    TYPING = 'typing'
    UPLOAD_PHOTO = 'upload_photo'
    RECORD_VIDEO = 'record_video'
    UPLOAD_VIDEO = 'upload_video'
    RECORD_VOICE = 'record_voice'
    UPLOAD_VOICE = 'upload_voice'
    UPLOAD_DOCUMENT = 'upload_document'
    CHOOSE_STICKER = 'choose_sticker'
    FIND_LOCATION = 'find_location'
    RECORD_VIDEO_NOTE = 'record_video_note'
    UPLOAD_VIDEO_NOTE = 'upload_video_note'
    
class ChatType(Enum):
    PRIVATE = 'private'
    GROUP = 'group'
    SUPERGROUP = 'supergroup'
    CHANNEL = 'channel'

class MessageOriginType(Enum):
    USER = 'user'
    HIDDEN_USER = 'hidden_user'
    CHAT = 'chat'
    CHANNEL = 'channel'

class PaidMediaType(Enum):
    PREVIEW = 'preview'
    PHOTO = 'photo'
    VIDEO = 'video'

class StickerType(Enum):
    REGULAR = 'regular'
    MASK = 'mask'
    CUSTOM_EMOJI = 'custom_emoji'

class MaskPositionPoint(Enum):
    FOREHEAD = 'forehead'
    EYES = 'eyes'
    MOUTH = 'mouth'
    CHIN = 'chin'

class MessageEntityType(Enum):
    MENTION = 'mention'
    HASHTAG = 'hashtag'
    CASHTAG = 'cashtag'
    BOT_COMMAND = 'bot_command'
    URL = 'url'
    EMAIL = 'email'
    PHONE_NUMBER = 'phone_number'
    BOLD = 'bold'
    ITALIC = 'italic'
    UNDERLINE = 'underline'
    STRIKETHROUGH = 'strikethrough'
    SPOILER = 'spoiler'
    BLOCKQUOTE = 'blockquote'
    EXPANDABLE_BLOCKQUOTE = 'expandable_blockquote'
    CODE = 'code'
    PRE = 'pre'
    TEXT_LINK = 'text_link'
    TEXT_MENTION = 'text_mention'
    CUSTOM_EMOJI = 'custom_emoji'

class UniqueGiftInfoOrigin(Enum):
    UPGRADE = 'upgrade'
    TRANSFER = 'transfer'

class EncryptedPassportElementType(Enum):
    PERSONAL_DETAILS = 'personal_details'
    PASSPORT = 'passport'
    DRIVER_LICENSE = 'driver_license'
    IDENTITY_CARD = 'identity_card'
    INTERNAL_PASSPORT = 'internal_passport'
    ADDRESS = 'address'
    UTILITY_BILL = 'utility_bill'
    BANK_STATEMENT = 'bank_statement'
    RENTAL_AGREEMENT = 'rental_agreement'
    PASSPORT_REGISTRATION = 'passport_registration'
    TEMPORARY_REGISTRATION = 'temporary_registration'
    PHONE_NUMBER = 'phone_number'
    EMAIL = 'email'

class BackgroundTypeFillType(Enum):
    FILL = 'fill'
    WALLPAPER = 'wallpaper'
    PATTERN = 'pattern'
    CHAT_THEME = 'chat_theme'

class BackgroundFillType(Enum):
    SOLID = 'solid'
    GRADIENT = 'gradient'
    FREEFORM_GRADIENT = 'freeform_gradient'