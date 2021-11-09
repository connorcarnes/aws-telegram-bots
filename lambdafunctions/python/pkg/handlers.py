def budget_bot_handler(event, context):
    message = json.loads(event["body"])
    send_message(str(message))

    # Check if edited_message key exists
    # Have not implemented any functionality around this,
    # but I want to know when it occurs
    if "edited_message" in message:
        send_message("Detected edited message. Doing nothing.")

    # Check if callback key exists
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
            put_item_dynamodb(callback_table, item)

        elif item["callback_data"] == "done":
            expense_amount = join_callback_data(callback_table, item)
            # Put item w/ expense_amount included into table
            item["expense_amount"] = expense_amount
            put_item_dynamodb(callback_table, item)
            # Have user confirm amount is correct
            confirm_expense_amount(expense_amount)

        elif item["callback_data"] == "yes":
            # expense_amount = join_callback_data(callback_table, item)
            # expense_amount = str(expense_amount)

            expense_amount = join_callback_data(callback_table, item)
            item["expense_amount"] = expense_amount
            put_item_dynamodb(data_table, item)
            ### TO DO: CLEAR ITEMS FROM CALLBACK TABLE

            send_message("Done!")

        elif item["callback_data"] == "no":
            send_message("Ok, resend the command and try again!")

        else:
            item_message = (
                "Hmm..Reached else statement in callback_query block. Item is: "
                + str(item)
            )
            send_message(item_message)

    # Check for message key
    elif "message" in message:
        # There are scenarios where multiple entities could be returned
        # But in the case of a bot command it's just one
        if "entities" in message["message"]:
            if len(message["message"]["entities"]) == 1:
                entity_type = message["message"]["entities"][0]["type"]
                message_text = message["message"]["text"]
                if (
                    entity_type == "bot_command"
                    and message_text == "/add_expense@BodaciousBudgetBot"
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
