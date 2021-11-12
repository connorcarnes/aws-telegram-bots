import json
import os
import requests
import boto3
from boto3.dynamodb.conditions import Attr


CHAT = os.environ["TG_CHAT"]
TOKEN = os.environ["TG_TOKEN"]
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CALLBACK_TABLE = os.environ["CALLBACK_TABLE"]
DATA_TABLE = os.environ["DATA_TABLE"]
BOT_NAME = os.environ["BOT_NAME"]
headers = {}
headers["Content-type"] = "application/json"
headers["charset"] = "UTF-8"
calc_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]


def send_message(text):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, CHAT)
    requests.post(url, headers)


def put_item_dynamodb(table_name, item):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    put_item = table.put_item(Item=item)
    if put_item["ResponseMetadata"]["HTTPStatusCode"] != 200:
        put_item_failed_message = "PUT ITEM FAILED: " + str(
            put_item["ResponseMetadata"]
        )
        send_message(put_item_failed_message)


def set_callback_item(
    update_id, callback_id, chat_id, callback_data, date, message_id, user_id
):
    return {
        "update_id": update_id,
        "callback_id": callback_id,
        "chat_id": chat_id,
        "callback_data": callback_data,
        "date": date,
        "message_id": message_id,
        "user_id": user_id,
    }


def join_callback_data(table_name, item):
    """
    Joins callback data values in the order they were entered and returns the value.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression=Attr("date").eq(item["date"])
        and Attr("message_id").eq(item["message_id"])
    )
    response["Items"].sort(key=lambda x: x["update_id"])
    expense_amount = []
    for i in response["Items"]:
        expense_amount.append(i["callback_data"])
    if expense_amount == "":
        send_message("You entered nothing.")
    else:
        return str("".join(expense_amount))


def confirm_expense_amount(expense_amount):
    button_one = {"text": "yes", "callback_data": "yes"}
    button_two = {"text": "no", "callback_data": "no"}
    row_one = [button_one, button_two]
    yes_no_keyboard = [row_one]
    reply_markup = {"inline_keyboard": yes_no_keyboard}
    reply_markup_json = json.dumps(reply_markup)
    msg = "You entered " + expense_amount + ", is this correct?"
    url = URL + "sendMessage?text={}&chat_id={}&reply_markup={}".format(
        msg, CHAT, reply_markup_json
    )
    request = requests.post(url, headers)
    if request.ok is not True:
        send_message(request.text)


def answer_callback_query(callback_id):
    url = URL + "answerCallbackQuery?callback_query_id={}".format(callback_id)
    callback_answer = requests.post(url, headers)
    if callback_answer.text != '{"ok":true,"result":true}':
        callback_answer_message = "CALLBACK RESULT: " + callback_answer.text
        send_message(callback_answer_message)


def send_numpad():
    button_one = {"text": "1", "callback_data": 1}
    button_two = {"text": "2", "callback_data": 2}
    button_three = {"text": "3", "callback_data": 3}
    button_four = {"text": "4", "callback_data": 4}
    button_five = {"text": "5", "callback_data": 5}
    button_six = {"text": "6", "callback_data": 6}
    button_seven = {"text": "7", "callback_data": 7}
    button_eight = {"text": "8", "callback_data": 8}
    button_nine = {"text": "9", "callback_data": 9}
    button_zero = {"text": "0", "callback_data": 0}
    button_dot = {"text": ".", "callback_data": "."}
    button_done = {"text": "done", "callback_data": "done"}
    row_one = [button_one, button_two, button_three]
    row_two = [button_four, button_five, button_six]
    row_three = [button_seven, button_eight, button_nine]
    row_four = [button_dot, button_zero, button_done]
    calc = [row_one, row_two, row_three, row_four]
    reply_markup = {"inline_keyboard": calc}
    reply_markup_json = json.dumps(reply_markup)
    msg = "Enter Amount:"
    url = URL + "sendMessage?text={}&chat_id={}&reply_markup={}".format(
        msg, CHAT, reply_markup_json
    )
    request = requests.post(url, headers)
    if request.ok is not True:
        send_message(request.text)


def budget_bot_handler(event, context):
    # message = json.loads(event["body"])
    message = json.loads(event)
    send_message(str(message))
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
            expense_amount = join_callback_data(CALLBACK_TABLE, item)
            item["expense_amount"] = expense_amount
            put_item_dynamodb(DATA_TABLE, item)
            send_message("Done!")
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
