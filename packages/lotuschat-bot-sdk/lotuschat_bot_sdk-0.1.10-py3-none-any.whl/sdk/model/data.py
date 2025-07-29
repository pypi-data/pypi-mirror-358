from typing import List, Optional, Union
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    is_bot: Optional[bool] = Field(default=None)
    language_code: Optional[str] = Field(default=None)
    profile_photos: Optional[str] = Field(default=None)


class MessageEntity(BaseModel):
    type: Optional[str] = Field(default=None)
    offset: Optional[int] = Field(default=None)
    length: Optional[int] = Field(default=None)
    url: Optional[str] = Field(default=None)
    user: Optional[User] = Field(default=None)


class ChatPhoto(BaseModel):
    file_id: Optional[str] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    file_size: Optional[int] = Field(default=None)
    link_cdn: Optional[str] = Field(default=None)


class Chat(BaseModel):
    id: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    photo: Optional[ChatPhoto] = Field(default=None)


class Message(BaseModel):
    message_id: Optional[int] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    date: Optional[int] = Field(default=None)
    chat: Optional[Chat] = Field(default=None)
    forward_from: Optional[User] = Field(default=None)
    forward_from_chat: Optional[Chat] = Field(default=None)
    forward_from_message_id: Optional[int] = Field(default=None)
    forward_date: Optional[int] = Field(default=None)
    reply_to_message: Optional[int] = Field(default=None)
    edit_date: Optional[int] = Field(default=None)
    text: Optional[str] = Field(default=None)
    entities: Optional[List[MessageEntity]] = Field(default=None)


class Updates(BaseModel):
    update_id: int
    message: Optional[Message] = Field(default=None)
    edited_message: Optional[Message] = Field(default=None)
    channel_post: Optional[Message] = Field(default=None)
    edited_channel_post: Optional[Message] = Field(default=None)
