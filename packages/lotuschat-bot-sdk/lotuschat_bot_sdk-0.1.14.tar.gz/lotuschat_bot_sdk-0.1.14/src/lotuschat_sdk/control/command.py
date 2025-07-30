import json
from typing import Dict, Any

import aiohttp

from src.lotuschat_sdk.control.bot import HEADERS, FAILED_REQUEST
from src.lotuschat_sdk.model.data import Command
from src.lotuschat_sdk.utility.logger import log_info, log_debug, log_warning


def command_action(cls):
    async def set_command(self, commands: list[Command]):
        log_info(f"set command {commands}")
        url = f"{self._domain}{self._token}/setMyCommands"
        encoded_commands = json.dumps([c.model_dump() for c in commands], ensure_ascii=False)
        payload: Dict[str | Any] = {
            "commands": encoded_commands,
        }
        log_debug(f"payload: {payload}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=HEADERS) as response:
                    response.raise_for_status()
                    text = await response.text()
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        result = text
                    log_debug(result)
                    return result
        except Exception as e:
            log_warning(FAILED_REQUEST.format("set_command", e))
            return None

    async def get_command(self):
        log_info(f"get command ")
        url = f"{self._domain}{self._token}/getMyCommands"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=HEADERS) as response:
                    response.raise_for_status()
                    text = await response.text()
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        result = text
                    log_debug(result)
                    return result
        except Exception as e:
            log_warning(FAILED_REQUEST.format("get_command", e))
            return None

    async def delete_command(self, commands: list[Command]):
        log_info(f"set command {commands}")
        url = f"{self._domain}{self._token}/deleteMyCommands"
        payload: Dict[str | Any] = {
            "commands": [command.model_dump() for command in commands],
        }
        log_debug(f"payload: {payload}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=HEADERS) as response:
                    response.raise_for_status()
                    text = await response.text()
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        result = text
                    log_debug(result)
                    return result
        except Exception as e:
            log_warning(FAILED_REQUEST.format("delete_command", e))
            return None

    # Attach async methods to the class
    cls.set_command = set_command
    cls.get_command = get_command
    cls.delete_command = delete_command
    return cls
