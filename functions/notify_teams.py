# https://medium.com/@sebastian.phelps/aws-cloudwatch-alarms-on-microsoft-teams-9b5239e23b64
import json
import logging
import os

import urllib3
from urllib.error import URLError, HTTPError

HOOK_URL = os.environ['TEAMS_WEBHOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    alarm_name = message['AlarmName']
    old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']

    base_data = {
        "colour": "64a837",
        "title": "**%s** is resolved" % alarm_name,
        "text": "**%s** has changed from %s to %s - %s" % (alarm_name, old_state, new_state, reason)
    }
    if new_state.lower() == 'alarm':
        base_data = {
            "colour": "d63333",
            "title": "Red Alert - There is an issue %s" % alarm_name,
            "text": "**%s** has changed from %s to %s - %s" % (alarm_name, old_state, new_state, reason)
        }

    messages = {
        ('ALARM', 'my-alarm-name'): {
            "colour": "d63333",
            "title": "Red Alert - A bad thing happened.",
            "text": "These are the specific details of the bad thing."
        },
        ('OK', 'my-alarm-name'): {
            "colour": "64a837",
            "title": "The bad thing stopped happening",
            "text": "These are the specific details of how we know the bad thing stopped happening"
        }
    }
    data = messages.get((new_state, alarm_name), base_data)

    message = {
      "@context": "https://schema.org/extensions",
      "@type": "MessageCard",
      "themeColor": data["colour"],
      "title": data["title"],
      "text": data["text"]
    }

    try:
        http = urllib3.PoolManager()
        response = http.request('POST', HOOK_URL, body=json.dumps(message).encode('utf-8'))
        logger.info("Message posted")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

