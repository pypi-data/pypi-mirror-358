from exam_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_SINGLE, CHAT_ID_GROUP
from src.sdk.control.bot import ChatBot, ParseModeType
from src.sdk.utility.logger import log_info


class Test:
    bot = ChatBot(
        name="Python Bot - Test message event",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    def run(self):
        log_info("send message to person")
        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person"
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="<b>python bot</b> send html message to <i>person</i>",
            parse_mode=ParseModeType.HTML
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="*python bot* send markdown message to _person_",
            parse_mode=ParseModeType.MARKDOWN
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with reply",
            reply_id=365
        )

        log_info("send message to group")
        self.bot.send_message(
            chat_id=CHAT_ID_GROUP,
            text="python bot send message to group"
        )
        self.bot.send_message(
            chat_id=CHAT_ID_GROUP,
            text="python bot send message to group with reply",
            reply_id = 365
        )


Test().run()
