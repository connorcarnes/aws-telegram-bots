from tgBudgetBot import *


# def test_handler(event, context):
#     message = "TO STRING: " + str(env_dict)
#     send_message(message)
#     return {"statusCode": 200}


def budget_bot_handler(event, context):
    message = json.loads(event["body"])
    # send_message(str(message))
    if "edited_message" in message:
        send_message("Detected edited message. Doing nothing.")
    elif "callback_query" in message:
        item = set_callback_item(
            update_id=message["update_id"],
            callback_id=message["callback_query"]["id"],
            chat_id=message["callback_query"]["message"]["chat"]["id"],
            callback_data=message["callback_query"]["data"],
            date=message["callback_query"]["message"]["date"],
            message_id=message["callback_query"]["message"]["message_id"],
            user_id=message["callback_query"]["from"]["id"],
        )
        answer_callback_query(item["callback_id"])
        if item["callback_data"] in calc_values:
            put_item_dynamodb(CALLBACK_TABLE, item)
        elif item["callback_data"] == "done":
            expense_amount = join_callback_data(CALLBACK_TABLE, item)
            item["expense_amount"] = expense_amount
            put_item_dynamodb(CALLBACK_TABLE, item)
            confirm_expense_amount(expense_amount)
        elif item["callback_data"] == "yes":
            expense_amount = get_latest_user_expense_amount(CALLBACK_TABLE, item)
            item["expense_amount"] = expense_amount
            put_item_dynamodb(DATA_TABLE, item)
            message = "Added expense of " + str(expense_amount) + " to the database."
            send_message(message)
        elif item["callback_data"] == "no":
            send_message("Ok, resend the command and try again!")
        else:
            item_message = (
                "Hmm..Reached else statement in callback_query block. Item is: "
                + str(item)
            )
            send_message(item_message)
    elif "message" in message:
        if "entities" in message["message"]:
            if len(message["message"]["entities"]) == 1:
                entity_type = message["message"]["entities"][0]["type"]
                message_text = message["message"]["text"]
                if (
                    entity_type == "bot_command"
                    and message_text == "/add_expense@" + BOT_NAME
                    or message_text == "/add_expense"
                ):
                    send_numpad()
                elif (
                    entity_type == "bot_command"
                    and message_text == "/get_my_expenses@" + BOT_NAME
                    or message_text == "/get_my_expenses"
                ):
                    item = {
                        "update_id": message["update_id"],
                        "chat_id": message["message"]["chat"]["id"],
                        "date": message["message"]["date"],
                        "message_id": message["message"]["message_id"],
                        "user_id": message["message"]["from"]["id"],
                    }
                    get_user_expenses(DATA_TABLE, item)
                else:
                    send_message("New bot command?")
        else:
            send_message("Message key exists, but no entities")
    else:
        item_message = (
            "No message, callback_query or edited_message key found. Message object is: "
            + str(message)
        )
        send_message(item_message)
    return {"statusCode": 200}
