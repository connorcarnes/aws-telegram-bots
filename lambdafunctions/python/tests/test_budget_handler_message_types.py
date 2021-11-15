"""
Telegram api returns unique keys in the message (update) object depending on the message type.
This test checks the correct actions are taken when certain unique keys are present


from shared.tgBudgetBot import *
from src.handlers import *


regular_message = {
    "update_id": 999,
    "message": {
        "message_id": 999,
        "from": {
            "id": 999,
            "is_bot": "false",
            "first_name": "first_name",
            "last_name": "last_name",
            "language_code": "en",
        },
        "chat": {
            "id": CHAT,
            "title": "chat_title",
            "type": "group",
            "all_members_are_administrators": "true",
        },
        "date": 1630893298,
        "text": "hi",
    },
}


class TestMessageTypes:
    def send_message(text):
        return text

    def test_regular_message(self):
        # LOOK HERE https://towardsdatascience.com/how-i-write-meaningful-tests-for-aws-lambda-functions-f009f0a9c587
        event = {}
        event["body"] = '{"update_id": 999, "edit_message": "hi"}'
        response = budget_bot_handler(event=event, context={})
        assert response == "Message key exists, but no entities"
"""
