from exam_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_SINGLE, CHAT_ID_GROUP
from src.sdk.control.bot import ChatBot
from src.sdk.model.data import InlineKeyboardMarkup, KeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    ForceReply, MessageEntity, ParseModeType
from src.sdk.utility.logger import log_info, log_debug


class Test:
    bot = ChatBot(
        name="Python Bot - Test message event",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    def run(self):
        log_info("get messages")
        log_debug(self.bot.get_messages(
            offset=0, limit=10
        ))

        log_debug(self.bot.get_messages(
            offset=0, limit=10, timeout=30
        ))

        log_debug(self.bot.get_messages(
            offset=0, limit=10, timeout=0
        ))

        log_debug(self.bot.get_messages(
            offset=0, limit=10, allowed_updates=["message"]
        ))

Test().run()
