from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

from flask import request

from ..model.data import Message, MessageEntity, Updates, BaseKeyboard, ParseModeType
from ..utility.logger import log_info, log_debug, log_error, log_verbose
from ..utility.utility import is_not_empty

FAILED_REQUEST = "Api[{}] request failed. Error: {}}"
RESPONSE_FOR_LC = "", 200
TYPE_BOT_COMMAND = "bot_command"
TYPE_UNKNOWN = "unknown"
TEXT_TYPE = "text"

@dataclass
class Argument:
    text: str
    type: str
    entity: Optional[MessageEntity] = None


class ChatBot:
    _command_listeners = {}

    def __init__(self, name, token, max_threads: int = 5, is_vpn=False):
        self._name = name
        self._token = token
        self._executor = ThreadPoolExecutor(max_workers=max_threads)
        self._error_listener = None
        self._self_messages_listener = None
        self._messages_listener = None
        self._messages_no_command_listener = None
        self._commands_listener = None
        if is_vpn:
            # dev mode
            self._domain = "http://bot.kingtalk.vn/bot"
        else:
            self._domain = "http://bot.lotuschat.vn/bot"

    def __str__(self):
        return f"Chatbot name[{self._name}] - token[{self._token}] - url[{self._domain}]"

    def set_on_messages(self, callback, is_get_command=True):
        log_info(f"register get all message")
        if is_get_command:
            self._messages_listener = callback
        else:
            self._messages_no_command_listener = callback

    def set_on_commands(self, callback):
        self._commands_listener = callback

    def set_on_command(self, command: str, callback):
        log_info(f"register command {command}")
        self._command_listeners[command] = callback

    def set_on_errors(self, callback):
        self._error_listener = callback

    def set_self_messages(self, callback):
        self._self_messages_listener = callback

    def web_hook(self):
        try:
            json = request.get_json()
            self._executor.submit(self._handle_message_hook, json)
        except Exception as e:
            log_error(f"web_hook has error: {e}")
            if self._error_listener: self._error_listener(f"web_hook has error: {e}")
        return RESPONSE_FOR_LC

    def _handle_message_hook(self, json):
        try:
            updates = self._get_message(json)
            is_valid_message = self._verify_message(updates)
            if is_valid_message:
                message = updates.message
                text = message.text
                from_user = message.from_user
                chat = message.chat

                if from_user.username == self._name:
                    if self._self_messages_listener:
                        self._self_messages_listener(text, chat.id, message)
                    return
                else:
                    if self._messages_listener:
                        self._messages_listener(text, chat.id, message)

                is_command = self._is_command(message)
                if is_command:
                    info = self._get_command(text=message.text, units=message.entities)
                    if info is None:
                        if self._messages_no_command_listener:
                            self._messages_no_command_listener(text, chat.id, message)
                    else:
                        command = info[0].text
                        args = info[1]
                        if self._commands_listener:
                            self._commands_listener(command, args, chat.id, message)
                        listener = self._command_listeners.get(command)
                        if listener:
                            listener(args, chat.id, message)
                else:
                    if self._messages_no_command_listener:
                        self._messages_no_command_listener(text, chat.id, message)
        except Exception as e:
            log_error(f"handle message has error: {e}")
            if self._error_listener: self._error_listener(f"handle message has error: {e}")

    def _get_message(self, json):
        log_info(f"{self} get message")
        log_verbose(json)
        if json:
            log_info(f"convert to Message class")
            updates = Updates(**json)
            log_debug(updates)
            return updates
        return None

    def _verify_message(self, updates: Updates):
        if updates is None:
            log_error(f"no receive message or response not json")
            if self._error_listener: self._error_listener(f"no receive message or response not json")
            return False
        message = updates.message
        if message is None:
            log_error(f"message no info, only update_id {updates.update_id}")
            if self._error_listener: self._error_listener(f"no receive message or response not json")
            return False
        if message.chat is None:
            log_error(f"not found chat object in message with update_id {updates.update_id}")
            return False
        if message.from_user is None:
            log_error(f"not found from object in message with update_id {updates.update_id}")
            return False
        return True

    def _is_command(self, message: Message):
        log_info(f"{self} check message is command or normal text")
        units = message.entities
        if units:
            for entity in units:
                if entity.type == TYPE_BOT_COMMAND and entity.offset == 0:
                    return True
        return False

    def _get_command(self, text: str, units: list[MessageEntity]):
        log_info(f"extract command")
        parts = self.entity_extract(text=text, units=units)
        if not parts:
            return None
        command = parts[0]
        args = parts[1:]
        return command, args

    def entity_extract(self, text: str, units: list[MessageEntity]) -> list[Argument]:
        log_info(f"{self} extract text @text")
        units = sorted(units, key=lambda e: e.offset)
        result = []
        cursor = 0

        for entity in units:
            if entity.type == TYPE_UNKNOWN:
                continue

            # Add plain text before the entity
            if cursor < entity.offset:
                temp = text[cursor:entity.offset].strip()
                if is_not_empty(temp):
                    result.append(Argument(temp, TEXT_TYPE, None))

            # Add the entity chunk
            end = entity.offset + entity.length
            temp = text[entity.offset:end].strip()
            result.append(Argument(temp, entity.type, entity))
            cursor = end

        # Add trailing text after last entity
        if cursor < len(text):
            temp = text[cursor:].strip()
            if is_not_empty(temp):
                result.append(Argument(temp, TEXT_TYPE, None))

        return result

    # interface message.py
    def get_messages(self, offset: int, limit: int, timeout: int = None, allowed_updates: list[str] = None):
        """Stub for IDE. Implemented in message.py."""

    def send_message(self, chat_id: int, text: str,
                     parse_mode: ParseModeType = None,
                     reply_to_message_id: int = None,
                     peer_id: int = None,
                     disable_web_page_preview: bool = None, disable_notification: bool = None,
                     reply_markup: BaseKeyboard = None,
                     entities: list[MessageEntity] = None):
        """Stub for IDE. Implemented in message.py."""

    def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""
