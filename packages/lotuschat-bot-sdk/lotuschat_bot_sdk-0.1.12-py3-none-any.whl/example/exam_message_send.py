from exam_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_SINGLE, CHAT_ID_GROUP
from src.sdk.control.bot import ChatBot
from src.sdk.model.data import InlineKeyboardMarkup, KeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    ForceReply, MessageEntity, ParseModeType
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
            reply_to_message_id=365
        )

        keyboard = [
            [
                KeyboardMarkup(text="Yes", callback_data="vote_yes"),
                KeyboardMarkup(text="No", callback_data="vote_no")
            ]
        ]
        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with InlineKeyboardMarkup",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with ReplyKeyboardMarkup",
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with clear ReplyKeyboardMarkup",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True, one_time_keyboard=True)
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with ReplyKeyboardRemove",
            reply_markup=ReplyKeyboardRemove(remove_keyboard=True)
        )

        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with force_reply",
            reply_markup=ForceReply(force_reply=True)
        )

        entities = [
            MessageEntity(
                offset=17, length=7, type="bold"
            ),
            MessageEntity(
                offset=34, length=6, type="text_link", url="https://example.com"
            )
        ]
        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send default message to person with entities",
            entities=entities
        )

        log_info("send message to group")
        self.bot.send_message(
            chat_id=CHAT_ID_GROUP,
            text="python bot send message to group"
        )
        self.bot.send_message(
            chat_id=CHAT_ID_GROUP,
            text="python bot send message to group with reply",
            reply_to_message_id=365
        )


Test().run()
