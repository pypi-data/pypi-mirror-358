import requests

from .bot import FAILED_REQUEST, ParseModeType
from ..utility.logger import log_info, log_warning, log_debug, log_verbose

def message_action(cls):
    def get_messages(self, offset: int, limit: int):
        log_info(f"getting messages with {offset}: {limit}")
        url = f"{self._domain}{self._token}/getUpdates"
        payload = {
            "offset": offset,
            "limit": limit
        }
        log_debug(payload)
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            json = response.json()
            log_verbose(json)
            return json
        except requests.RequestException as e:
            log_warning(FAILED_REQUEST.format("get_messages", e))
            return None

    def send_message(self, chat_id: int, text: str, parse_mode: str = ParseModeType.HTML, reply_id: int = None):
        log_info(f"sending message to {chat_id}: {text}")
        url = f"{self._domain}{self._token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_id:
            payload["reply_to_message_id"] = reply_id
        log_debug(f"payload: {payload}")
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            json = response.json()
            log_verbose(json)
            return json
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
                json = response.json()
                log_verbose(json)
                return json
            except requests.RequestException as e:
                log_warning(FAILED_REQUEST.format("send_document", e))
                return None

    cls.get_messages = get_messages
    cls.send_message = send_message
    cls.send_document = send_document
