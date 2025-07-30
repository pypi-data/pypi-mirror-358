from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional, Union
from ... import Enums


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None

class Chat(BaseModel):
    id: int
    type: Enums.ChatType
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_forum: Optional[bool] = None

class _MessageOrigin(BaseModel):
    type: Enums.MessageOriginType
    date: int

class MessageOriginUser(_MessageOrigin):
    sender_user: User

class MessageOriginHiddenUser(_MessageOrigin):
    sender_user_name: str

class MessageOriginChat(_MessageOrigin):
    sender_chat: Chat
    author_signature: Optional[str] = None

class MessageOriginChannel(_MessageOrigin):
    chat: Chat
    message_id: int
    author_signature: Optional[str] = None

MessageOrigin = Union[
    MessageOriginUser,
    MessageOriginHiddenUser,
    MessageOriginChat,
    MessageOriginChannel
]

class LinkPreviewOptions(BaseModel):
    is_disabled: Optional[bool] = None
    url: Optional[str] = None
    prefer_small_media: Optional[bool] = None
    prefer_large_media: Optional[bool] = None
    show_above_text: Optional[bool] = None

class PhotoSize(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int]

class Animation(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class Audio(BaseModel):
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumbnail: Optional[PhotoSize] = None

class Document(BaseModel):
    file_id: str
    file_unique_id: str
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class Video(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    cover: Optional[list[PhotoSize]] = []
    start_timestamp: Optional[int] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None



class _PaidMedia(BaseModel):
    type: Enums.PaidMediaType

class PaidMediaPreview(_PaidMedia):
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    
class PaidMediaPhoto(_PaidMedia):
    photo: list[PhotoSize]

class PaidMediaVideo(_PaidMedia):
    video: Video

PaidMedia = Union[
    PaidMediaPreview,
    PaidMediaPhoto,
    PaidMediaVideo
]

class PaidMediaInfo(BaseModel):
    star_count: int
    paid_media: list[PaidMedia]

class File(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None

class MaskPosition(BaseModel):
    point: Enums.MaskPositionPoint
    x_shift: float
    y_shift: float
    scale: float

class Sticker(BaseModel):
    file_id: str
    file_unique_id: str
    type: Enums.StickerType
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumbnail: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    premium_animation: Optional[File]
    mask_position: Optional[MaskPosition] = None
    custom_emoji_id: Optional[str] = None
    needs_repainting: Optional[bool] = None
    file_size: Optional[int] = None

class Story(BaseModel):
    chat: Chat
    id: int

class VideoNote(BaseModel):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    file_size: Optional[int] = None

class Voice(BaseModel):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class Contact(BaseModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[str] = None

class Dice(BaseModel):
    emoji: str
    value: int

class MessageEntity(BaseModel):
    type: Enums.MessageEntityType
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None

class Game(BaseModel):
    title: str
    description: str
    photo: list[PhotoSize]
    text: Optional[str] = None
    text_entities: Optional[list[MessageEntity]] = []
    animation: Optional[Animation] = None

class Giveaway(BaseModel):
    chats: list[Chat]
    winners_selection_date: int
    winner_count: int
    only_new_members: Optional[bool] = None
    has_public_winners: Optional[bool] = None
    prize_description: Optional[str] = None
    country_codes: Optional[list[str]] = []
    prize_star_count: Optional[int] = None
    premium_subscription_month_count: Optional[int] = None

class GiveawayWinners(BaseModel):
    chat: Chat
    giveaway_message_id: int
    winners_selection_date: int
    winner_count: int
    winners: list[User]
    additional_chat_count: Optional[int] = None
    prize_star_count: Optional[int] = None
    premium_subscription_month_count: Optional[int] = None
    unclaimed_prize_count: Optional[int] = None
    only_new_members: Optional[int] = None
    was_refunded: Optional[bool] = None
    prize_description: Optional[str] = None

class Invoice(BaseModel):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int

class Location(BaseModel):
    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None

class PollOption(BaseModel):
    text: str
    text_entities: Optional[list[MessageEntity]] = []
    voter_count: int

class PollType(Enum):
    regular = 'regular'
    quiz = 'quiz'

class Poll(BaseModel):
    id: str
    question: str
    question_entities: Optional[list[MessageEntity]] = []
    options: list[PollOption]
    total_voter_count: int
    is_closed: bool 
    is_anonymous: bool
    type: PollType
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[list[MessageEntity]] = []
    open_period: Optional[int] = None
    close_date: Optional[int] = None

class Venue(BaseModel):
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None

class ExternalReplyInfo(BaseModel):
    origin: MessageOrigin
    chat: Optional[Chat] = None
    message_id: Optional[int] = None
    link_preview_options: Optional[LinkPreviewOptions] = None
    animation: Optional[Animation] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    paid_media: Optional[PaidMediaInfo] = None
    photo: Optional[list[PhotoSize]] = []
    sticker: Optional[Sticker] = None
    story: Optional[Story] = None
    video: Optional[Video] = None
    video_note: Optional[VideoNote] = None
    voice: Optional[Voice] = None
    has_media_spoiler: Optional[bool] = None
    contact: Optional[Contact] = None
    dice: Optional[Dice] = None
    game: Optional[Game] = None
    giveaway: Optional[Giveaway] = None
    giveaway_winners: Optional[GiveawayWinners] = None
    invoice: Optional[Invoice] = None
    location: Optional[Location] = None
    poll: Optional[Poll] = None
    venue: Optional[Venue] = None

class TextQuote(BaseModel):
    text: str
    entities: Optional[list[MessageEntity]] = []
    position: int
    is_manual: Optional[bool] = None

class MessageAutoDeleteTimerChanged(BaseModel):
    message_auto_delete_time: int

class InaccessibleMessage(BaseModel):
    chat: Chat
    message_id: int
    date: int

MaybeInaccessibleMessage = Union[
    'Message',
    InaccessibleMessage
]

class ShippingAddress(BaseModel):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str

class OrderInfo(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None

class SuccessfulPayment(BaseModel):
    currency: str
    total_amount: int
    invoice_payload: str
    subscription_expiration_date: Optional[int] = None
    is_recurring: Optional[bool] = None
    is_first_recurring: Optional[bool] = None
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None
    telegram_payment_charge_id: str
    provider_payment_charge_id: str

class RefundedPayment(BaseModel):
    currency: str
    total_amount: int
    invoice_payload: str    
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    
class SharedUser(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo: Optional[list[PhotoSize]] = []
    
class UsersShared(BaseModel):
    request_id: int
    users: list[SharedUser]

class ChatShared(BaseModel):
    request_id: int
    chat_id: int
    title: Optional[str] = None
    username: Optional[str] = None
    photo: Optional[list[PhotoSize]] = []

class Gift(BaseModel):
    id: str
    sticker: Sticker
    star_count: int
    upgrade_star_count: Optional[int] = None
    total_count: Optional[int] = None
    remaining_count: Optional[int] = None

class GiftInfo(BaseModel):
    gift: Gift
    owned_gift_id: Optional[str] = None
    convert_star_count: Optional[int] = None
    prepaid_upgrade_star_count: Optional[int] = None
    can_be_upgraded: Optional[bool] = False
    text: Optional[str] = None
    entities: Optional[list[MessageEntity]] = []
    is_private: Optional[bool] = False

class _UniqueGift(BaseModel):
    name: str 
    rarity_per_mille: int

class UniqueGiftModel(_UniqueGift):
    sticker: Sticker
    
class UniqueGiftSymbol(_UniqueGift):
    sticker: Sticker

class UniqueGiftBackdropColors(BaseModel):
    center_color: int
    edge_color: int
    symbol_color: int
    text_color: int

class UniqueGiftBackdrop(_UniqueGift):
    colors: UniqueGiftBackdropColors

class UniqueGift(BaseModel):
    base_name: str
    name: str
    number: int
    model: UniqueGiftModel
    symbol: UniqueGiftSymbol
    backdrop: UniqueGiftBackdrop

class UniqueGiftInfo(BaseModel):
    gift: UniqueGift
    origin: Enums.UniqueGiftInfoOrigin
    owned_gift_id: Optional[str] = None
    transfer_star_count: Optional[int] = None

class WriteAccessAllowed(BaseModel):
    from_request: Optional[bool] = None
    web_app_name: Optional[str] = None
    from_attachment_menu: Optional[bool] = None

class PassportFile(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: int
    file_date: int

class EncryptedPassportElement(BaseModel):
    type: Enums.EncryptedPassportElementType
    data: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    files: Optional[list[PassportFile]] = []
    front_side: Optional[PassportFile] = None
    reverse_side: Optional[PassportFile] = None
    selfie: Optional[PassportFile] = None
    translation: Optional[list[PassportFile]] = []
    hash: str

class EncryptedCredentials(BaseModel):
    data: str
    hash: str
    secret: str

class PassportData(BaseModel):
    data: list[EncryptedPassportElement]
    credentials: EncryptedCredentials

class ProximityAlertTriggered(BaseModel):
    traveler: User
    watcher: User
    distance: int

class ChatBoostAdded(BaseModel):
    boost_count: int

class _BackgroundTypeFill(BaseModel):
    type: Enums.BackgroundTypeFillType

class _BackgroundFill(BaseModel):
    type: Enums.BackgroundFillType

class BackgroundFillSolid(_BackgroundFill):
    color: int
    
class BackgroundFillGradient(_BackgroundFill):
    top_color: int
    bottom_color: int
    rotation_angle: int
    
class BackgroundFillFreeformGradient(_BackgroundFill):
    colors: list[int]
    

BackgroundFill = Union[
    BackgroundFillSolid,
    BackgroundFillGradient,
    BackgroundFillFreeformGradient,
]

class BackgroundTypeFill(_BackgroundTypeFill):
    fill: BackgroundFill
    dark_theme_dimming: int
    
class BackgroundTypeWallpaper(_BackgroundTypeFill):
    document: Document
    dark_theme_dimming: int
    is_blurred: Optional[bool] = None
    is_moving: Optional[bool] = None
    
class BackgroundTypePattern(_BackgroundTypeFill):
    document: Document
    fill: BackgroundFill
    intensity: int
    is_inverted: Optional[bool] = None
    is_moving: Optional[bool] = None
    
class BackgroundTypeChatTheme(_BackgroundTypeFill):
    theme_name: str
    
BackgroundType = Union[
    BackgroundTypeFill,
    BackgroundTypeWallpaper,
    BackgroundTypePattern,
    BackgroundTypeChatTheme,
]

class ChatBackground(BaseModel):
    type: BackgroundType

class ForumTopicCreated(BaseModel):
    name: str
    icon_color: int
    icon_custom_emoji_id: Optional[str] = None

class ForumTopicEdited(BaseModel):
    name: Optional[str]
    icon_custom_emoji_id: Optional[str] = None

class GiveawayCreated(BaseModel):
    prize_star_count: Optional[int] = None

class GiveawayCompleted(BaseModel):
    winner_count: int
    unclaimed_prize_count: Optional[int] = None
    giveaway_message: Optional['Message'] = None
    is_star_giveaway: Optional[bool] = None

class PaidMessagePriceChanged(BaseModel):
    paid_message_star_count: int

class VideoChatScheduled(BaseModel):
    start_date: int

class VideoChatEnded(BaseModel):
    duration: int

class VideoChatParticipantsInvited(BaseModel):
    users: list[User]

class WebAppData(BaseModel):
    data: str
    button_text: str

class WebAppInfo(BaseModel):
    url: str

class LoginUrl(BaseModel):
    url: str
    forward_text: Optional[str] = None
    bot_username: Optional[str] = None
    request_write_access: Optional[bool] = None

class SwitchInlineQueryChosenChat(BaseModel):
    query: Optional[str] = None
    allow_user_chats: Optional[bool] = None
    allow_bot_chats: Optional[bool] = None
    allow_group_chats: Optional[bool] = None
    allow_channel_chats: Optional[bool] = None

class CopyTextButton(BaseModel):
    text: str

class InlineKeyboardButton(BaseModel):
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None
    web_app: Optional[WebAppInfo] = None
    login_url: Optional[LoginUrl] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    switch_inline_query_chosen_chat: Optional[SwitchInlineQueryChosenChat] = None
    copy_text: Optional[CopyTextButton] = None
    callback_game: Optional[str] = None #Optional[CallbackGame] = None
    pay: Optional[bool] = None

class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]

class KeyboardButtonRequestUsers(BaseModel):
    request_id: int
    user_is_bot: Optional[bool] = None
    user_is_premium: Optional[bool] = None
    max_quantity: Optional[int] = None
    request_name: Optional[bool] = None
    request_username: Optional[bool] = None
    request_photo: Optional[bool] = None

class ChatAdministratorRights(BaseModel):
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_stories: bool
    can_edit_stories: bool
    can_delete_stories: bool
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_manage_topics: Optional[bool] = None

class KeyboardButtonRequestChat(BaseModel):
    request_id: int
    chat_is_channel: bool
    chat_is_forum: Optional[bool] = None
    chat_has_username: Optional[bool] = None
    chat_is_created: Optional[bool] = None
    user_administrator_rights: Optional[ChatAdministratorRights] = None
    bot_administrator_rights: Optional[ChatAdministratorRights] = None
    bot_is_member: Optional[bool] = None
    request_title: Optional[bool] = None
    request_username: Optional[bool] = None
    request_photo: Optional[bool] = None

class KeyboardButtonPollType(BaseModel):
    type: Optional[str] = None

class KeyboardButton(BaseModel):
    text: str
    request_users: Optional[KeyboardButtonRequestUsers] = None
    request_chat: Optional[KeyboardButtonRequestChat] = None
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None
    request_poll: Optional[KeyboardButtonPollType] = None
    web_app: Optional[WebAppInfo] = None

class ReplyKeyboardMarkup(BaseModel):
    keyboard: list[list[KeyboardButton]]
    is_persistent: Optional[bool] = None
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = None

class ReplyKeyboardRemove(BaseModel):
    remove_keyboard: bool = True
    selective: Optional[bool] = None

class ForceReply(BaseModel):
    force_reply: bool = True
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = None

class Message(BaseModel):
    message_id: int
    message_thread_id: Optional[int] = None
    from_user: Optional[User] = Field(default=None, alias='from') 
    sender_chat: Optional[Chat] = None
    sender_boost_count: Optional[int] = None
    sender_business_bot: Optional[User] = None
    date: int
    business_connection_id: Optional[str] = None
    chat: Chat
    forward_origin: Optional[MessageOrigin] = None
    is_topic_message: Optional[bool] = None
    is_automatic_forward: Optional[bool] = None
    reply_to_message: Optional['Message'] = None
    external_reply: Optional[ExternalReplyInfo] = None
    quote: Optional[TextQuote] = None
    reply_to_story: Optional[Story] = None
    via_bot: Optional[User] = None
    edit_date: Optional[int] = None
    has_protected_content: Optional[bool] = None
    is_from_offline: Optional[bool] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    paid_star_count: Optional[int] = None
    text: Optional[str] = None
    entities: Optional[list[MessageEntity]] = []
    link_preview_options: Optional[LinkPreviewOptions] = None
    effect_id: Optional[str] = None
    animation: Optional[Animation] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    paid_media: Optional[PaidMediaInfo] = None
    photo: Optional[list[PhotoSize]] = []
    sticker: Optional[Sticker] = None
    story: Optional[Story] = None
    video: Optional[Video] = None
    video_note: Optional[VideoNote] = None
    voice: Optional[Voice] = None
    caption: Optional[str] = None
    caption_entities: Optional[list[MessageEntity]] = []
    show_caption_above_media: Optional[bool] = None
    has_media_spoiler: Optional[bool] = None
    contact: Optional[Contact] = None
    dice: Optional[Dice] = None
    game: Optional[Game] = None
    poll: Optional[Poll] = None
    venue: Optional[Venue] = None
    location: Optional[Location] = None
    new_chat_members: Optional[list[User]] = []
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[list[PhotoSize]] = []
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    channel_chat_created: Optional[bool] = None
    message_auto_delete_timer_changed: Optional[MessageAutoDeleteTimerChanged] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    pinned_message: Optional[MaybeInaccessibleMessage] = None
    invoice: Optional[Invoice] = None
    successful_payment: Optional[SuccessfulPayment] = None
    refunded_payment: Optional[RefundedPayment] = None
    users_shared: Optional[UsersShared] = None
    chat_shared: Optional[ChatShared] = None
    gift: Optional[GiftInfo] = None
    unique_gift: Optional[UniqueGiftInfo] = None
    connected_website: Optional[str] = None
    write_access_allowed: Optional[WriteAccessAllowed] = None
    passport_data: Optional[PassportData] = None
    proximity_alert_triggered: Optional[ProximityAlertTriggered] = None
    boost_added: Optional[ChatBoostAdded] = None
    chat_background_set: Optional[ChatBackground] = None
    forum_topic_created: Optional[ForumTopicCreated] = None
    forum_topic_edited: Optional[ForumTopicEdited] = None
    forum_topic_closed: Optional[str] = None #Optional[ForumTopicClosed] = None
    forum_topic_reopened: Optional[str] = None #Optional[ForumTopicReopened] = None
    general_forum_topic_hidden: Optional[str] = None #Optional[GeneralForumTopicHidden] = None
    general_forum_topic_unhidden: Optional[str] = None #Optional[GeneralForumTopicUnhidden] = None
    giveaway_created: Optional[GiveawayCreated] = None
    giveaway: Optional[Giveaway] = None
    giveaway_winners: Optional[GiveawayWinners] = None
    giveaway_completed: Optional[GiveawayCompleted] = None
    paid_message_price_changed: Optional[PaidMessagePriceChanged] = None
    video_chat_scheduled: Optional[VideoChatScheduled] = None
    video_chat_started: Optional[str] = None #Optional[VideoChatStarted] = None
    video_chat_ended: Optional[VideoChatEnded] = None
    video_chat_participants_invited: Optional[VideoChatParticipantsInvited] = None
    web_app_data: Optional[WebAppData] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None

class ReplyParameters(BaseModel):
    message_id: int
    chat_id: int | str
    allow_sending_without_reply: Optional[bool] = None
    quote: Optional[str] = None
    quote_parse_mode: Optional[Enums.ParseMode] = None
    quote_entities: Optional[list[MessageEntity]] = None
    quote_position: Optional[int] = None

class CallbackQuery(BaseModel):
    id: str
    chat_instance: str
    from_user: User = Field(alias='from')
    message: Optional[MaybeInaccessibleMessage] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None

