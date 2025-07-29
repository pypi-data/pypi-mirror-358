from typing import Dict, Any

import requests

from .bot import FAILED_REQUEST
from ..model.data import MessageEntity, BaseKeyboard, ParseModeType
from ..utility.logger import log_info, log_warning, log_debug, log_verbose


def message_action(cls):
    def get_messages(self, offset: int, limit: int, timeout: int = None, allowed_updates: list[str] = None):
        log_info(f"getting messages with {offset}: {limit}")
        if offset < 0: offset = 0
        if limit < 0: limit = 10
        url = f"{self._domain}{self._token}/getUpdates"
        payload: Dict[str | Any] = {
            "offset": offset,
            "limit": limit
        }
        if timeout:
            if timeout < 0: timeout = 0
            payload["timeout"] = timeout
        if allowed_updates:
            payload["allowed_updates"] = allowed_updates
        log_debug(payload)
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            log_verbose(result)
            return result
        except requests.RequestException as e:
            log_warning(FAILED_REQUEST.format("get_messages", e))
            return None

    def send_message(self, chat_id: int, text: str,
                     parse_mode: ParseModeType = None,
                     reply_to_message_id: int = None,
                     peer_id: int = None,
                     disable_web_page_preview: bool = None,
                     disable_notification: bool = None,
                     reply_markup: BaseKeyboard = None,
                     entities: list[MessageEntity] = None):
        log_info(f"sending message to {chat_id}: {text}")
        url = f"{self._domain}{self._token}/sendMessage"
        payload: Dict[str | Any] = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode.value
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if peer_id:
            payload["peer_id"] = peer_id
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = disable_web_page_preview
        if disable_notification:
            payload["disable_notification"] = disable_notification
        if reply_markup and reply_markup is not BaseKeyboard:
            payload["reply_markup"] = reply_markup.model_dump()
        if entities:
            payload["entities"] = [entity.model_dump() for entity in entities]
        log_debug(f"payload: {payload}")
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            log_verbose(result)
            return result
        except requests.RequestException as e:
            log_warning(FAILED_REQUEST.format("send_message", e))
            return None

    def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None):
        log_info(f"logging in user {chat_id}: {file_path} - {caption}")
        url = f"{self._domain}{self._token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {"document": file}
            data = {
                "chat_id": f"{chat_id}",
            }
            if caption:
                data['caption'] = caption
            if reply_id:
                data["reply_to_message_id"] = f"{reply_id}"
            log_debug(data)
            try:
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                result = response.json()
                log_verbose(result)
                return result
            except requests.RequestException as e:
                log_warning(FAILED_REQUEST.format("send_document", e))
                return None

    cls.get_messages = get_messages
    cls.send_message = send_message
    cls.send_document = send_document
