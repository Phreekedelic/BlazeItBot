import os
import json
import requests

######################
# helper functions
######################
# recursively look/return for an item in dict given key


def find_item(obj, key):
    item = None
    if key in obj:
        return obj[key]

    for k, v in obj.items():
        if isinstance(v, dict):

            item = find_item(v, key)
            if item is not None:
                return item

# recursively check for items in a dict given key


def keys_exist(obj, keys):
    for key in keys:
        if find_item(obj, key) is None:
            return False
    return True

# send txt via messenger to id

def send_message(send_id, msg_txt):
    params = {"access_token": os.environ['access_token']}

    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {"id": send_id},
                       "message": {"text": msg_txt}})

    response = requests.post("https://graph.facebook.com/v2.6/me/messages",
                             params=params, headers=headers, data=data)

    if response.status_code != 200:
        print(response.status_code)
        print(response.text)


def request_broadcast():
    params = {"access_token": os.environ['access_token']}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"messages": [{"dynamic_text": {
                      "text": "Hey {{first_name}}, it's 420- blaze it.", "fallback_text": "It's 420- blaze it."}}]})


    response = requests.post("https://graph.facebook.com/v2.11/me/message_creatives",
                             params=params, headers=headers, data=data)

    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
    else:
        data = json.dumps(
            {"message_creative_id": response.json()['message_creative_id']})

        broadcastResponse = requests.post(
            "https://graph.facebook.com/v2.11/me/broadcast_messages",
            params=params, headers=headers, data=data)

        if broadcastResponse.status_code != 200:
            print(broadcastResponse.status_code)
            print(broadcastResponse.text)


# -----------------------------------------------------------


def lambda_handler(event, context):
    # handle webhook challenge
    if keys_exist(event, ["params", "querystring", "hub.verify_token", "hub.challenge"]):
        v_token = str(find_item(event, 'hub.verify_token'))
        challenge = int(find_item(event, 'hub.challenge'))
        if os.environ['verify_token'] == v_token:
            return challenge

    # handle messaging events
    if keys_exist(event, ['body-json', 'entry']):
        event_entry0 = event['body-json']['entry'][0]
        if keys_exist(event_entry0, ['messaging']):
            messaging_event = event_entry0['messaging'][0]
            msg_txt = messaging_event['message']['text']
            sender_id = messaging_event['sender']['id']
            send_message(sender_id, msg_txt)
    elif keys_exist(event, ['source', 'resources']):
        request_broadcast()
    return None
