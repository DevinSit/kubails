import json
import logging
import requests
from typing import Dict, List


logger = logging.getLogger(__name__)


class Slack:
    def __init__(self):
        pass

    def send_message(
        self,
        webhook: str,
        title: str,
        fields: List[Dict[str, str]],
        color: str
    ) -> bool:
        data = {
            "attachments": [
                {
                    "title": title,
                    "fields": fields,
                    "color": color
                }
            ]
        }

        response = requests.post(
            webhook,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            logger.error("Failed to send Slack message: {}".format(response.content))
            return False
        else:
            return True
