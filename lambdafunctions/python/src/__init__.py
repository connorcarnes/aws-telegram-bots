import json
import os
import requests
import boto3
from boto3.dynamodb.conditions import Attr


# https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
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
    # request_json = request.json()
    # print(url)
    # print(headers)
    # print(request.status_code)
    # print(request.text)


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
    Joins callback data values in the order they were entered and returns the value
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    # Scan table for items matching the date and message_id of callback_item
    response = table.scan(
        FilterExpression=Attr("date").eq(item["date"])
        and Attr("message_id").eq(item["message_id"])
    )
    # Sort items by the time they were entered to return the correct expense_amount
    # We can rely on update_id for this as it's incremented chronologically
    response["Items"].sort(key=lambda x: x["update_id"])
    expense_amount = []
    # Iterate through the sorted items to append them to an array
    for i in response["Items"]:
        # print(i['update_id'], ":", i['date'], ":", i['message_id'], ":", i['callback_data'])
        expense_amount.append(i["callback_data"])
    # If nothing was entered, return message stating the same
    if expense_amount == "":
        send_message("You entered nothing.")
    # Else join items from array into a float and return the amount entered
    else:
        # Can't use boto3 to put floats in dynamodb
        # https://github.com/boto/boto3/issues/665
        return str("".join(expense_amount))


def confirm_expense_amount(expense_amount):
    # yes_no_keyboard
    button_one = {"text": "yes", "callback_data": "yes"}
    button_two = {"text": "no", "callback_data": "no"}
    row_one = [button_one, button_two]
    yes_no_keyboard = [row_one]
    reply_markup = {"inline_keyboard": yes_no_keyboard}
    reply_markup_json = json.dumps(reply_markup)
    # yes_no_keyboard
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
    # Numberpad Data
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
    # Numberpad Data
    msg = "Enter Amount:"
    url = URL + "sendMessage?text={}&chat_id={}&reply_markup={}".format(
        msg, CHAT, reply_markup_json
    )
    request = requests.post(url, headers)
    if request.ok is not True:
        send_message(request.text)
