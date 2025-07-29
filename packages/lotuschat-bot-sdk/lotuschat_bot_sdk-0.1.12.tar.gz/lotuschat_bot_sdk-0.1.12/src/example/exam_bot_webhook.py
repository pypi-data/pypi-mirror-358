from flask import Flask

from exam_const import TOKEN_STICKER_DOWNLOAD_BOT
from src.sdk.control import ChatBot
from src.sdk.control.bot import Argument
from src.sdk.model.data import Message
from src.sdk.utility.logger import log_verbose, log_debug, log_info, log_warning


# Class testing
class Test:
    bot = ChatBot(
        name="sticker_download_bot",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    def on_errors(self, error):
        log_warning(f"function{self} receive error from bot: {error}")

    def on_self_messages(self, text: str, chat_id: int, message: Message):
        log_verbose(f"function{self} receive this bot {chat_id} message {text}")

    def on_messages(self,  text: str, chat_id: int, message: Message):
        log_verbose(f"function{self} receive all message with message[{text}] from {chat_id}")
        if message.entities:
            result = self.bot.entity_extract(text, message.entities)
            log_debug(result)

    def on_messages_no_command(self, text: str, chat_id: int, message: Message):
        log_verbose(f"function{self} receive all message with no command with message[{text}] from {chat_id}")

    def on_commands(self, command: str, args: list[Argument], chat_id: int, message: Message):
        log_verbose(f"function{self} receive all command with command {command} from {chat_id} has arguments {args}")

    def on_temp_command(self, args: list[Argument], chat_id: int, message: Message):
        log_verbose(f"function{self} handle temp command with arguments {args} from {chat_id}")

    def run(self):
        log_info(f"create bot[{self}] to test send message")
        log_debug(self.bot)

        log_info("setting listener & receive message event")
        self.bot.set_on_errors(self.on_errors)
        self.bot.set_self_messages(self.on_self_messages)
        self.bot.set_on_messages(self.on_messages)
        self.bot.set_on_messages(self.on_messages_no_command, is_get_command=False)
        self.bot.set_on_commands(self.on_commands)
        self.bot.set_on_command("/temp", self.on_temp_command)


# Running
control = Test()

app = Flask(__name__)


@app.route("/", methods=["POST"])
def lc_webhook():
    return control.bot.web_hook()


if __name__ == "__main__":
    control.run()
    app.run(port=4800)
