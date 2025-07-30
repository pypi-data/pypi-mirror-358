import contextlib

from telegram import Update

from project.other_module import func_for_other_actor

@contextlib.contextmanager
def transaction():
    ...

class Message:
    def __init__(self, id: int, response: str, text: str): ...

def save_messages(
    id: int, text: str, response: str
):
    with transaction() as db:
        message = Message(id, response, text)
        db.add(message)


def create_answer(question: str) -> str:
    func_for_other_actor()
    return "Answer"


def generate_message(update: Update):
    response = create_answer(update.message.text)

    save_messages(
        update.effective_user.id,
        response,
        update.message.text,
    )

    update.message.reply_text(response)
