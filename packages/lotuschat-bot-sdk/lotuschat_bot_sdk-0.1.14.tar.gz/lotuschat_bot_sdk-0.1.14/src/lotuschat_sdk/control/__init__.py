from ..control.bot import ChatBot
from ..control.message import message_action
from ..control.command import command_action

message_action(ChatBot)
command_action(ChatBot)

__all__ = ["ChatBot"]