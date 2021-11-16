import json
import os
import requests
import boto3
from boto3.dynamodb.conditions import Attr


CHAT = os.environ["CHAT_ID"]
TOKEN = os.environ["BOT_TOKEN"]
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CALLBACK_TABLE = os.environ["CALLBACK_TABLE"]
DATA_TABLE = os.environ["DATA_TABLE"]
BOT_NAME = os.environ["BOT_NAME"]
headers = {}
headers["Content-type"] = "application/json"
headers["charset"] = "UTF-8"
calc_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]


def send_message(text, parse_mode=""):
    if parse_mode == "":
        url = URL + "sendMessage?text={}&chat_id={}".format(text, CHAT)
    else:
        url = URL + "sendMessage?text={}&chat_id={}&parse_mode={}".format(
            text, CHAT, parse_mode
        )
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
    update_id, chat_id, date, message_id, user_id, callback_id="", callback_data=""
):
    return {
        "update_id": update_id,
        "chat_id": chat_id,
        "date": date,
        "message_id": message_id,
        "user_id": user_id,
        "callback_id": callback_id,
        "callback_data": callback_data,
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


def get_latest_user_expense_amount(table_name, item):
    """
    Gets items from the callback table that have the specified user_id and an expense_amount,
    sorts them by date and returns the latest one.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression=Attr("user_id").eq(item["user_id"])
        and Attr("expense_amount").exists()
    )
    # Get the most recent expense
    response["Items"].sort(reverse=True, key=lambda x: x["date"])
    return response["Items"][0]["expense_amount"]


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


def get_user_expenses(table_name, item):
    """
    Gets all the expenses for the specified user.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression=Attr("user_id").eq(item["user_id"])
        and Attr("expense_amount").exists()
    )

    table = "Time" + ": " + "Amount" + "\n"
    for x in response["Items"]:
        date = datetime.utcfromtimestamp(x["date"].__int__()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        amount = x["expense_amount"]
        entry = date + ": " + amount + "\n"
        table += entry

    message = "<pre>" + table + "</pre>"
    send_message(message, "HTML")


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
