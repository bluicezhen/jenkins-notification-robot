import json
import requests
import web
from urllib.parse import parse_qs


urls = (
    '/', 'NotificationRobot'
)

app = web.application(urls, globals())


class NotificationRobot:

    def POST(self):
        data = json.loads(web.data())

        if data['build']['phase'] in ['QUEUED', 'STARTED', 'FINALIZED']:
            # Get Feishu webhook URL.
            try:
                feishu_webhook = parse_qs(data['build']['notes'])['feishu_webhook'][0]
            except KeyError:
                print(
                    f'Can Not found feishu_webhook in build.notes: {data["build"]["full_url"]}')
                return

            # Send Feishu notification
            feishu_msg = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "template": {
                            'STARTED': lambda : 'blue',
                            'FINALIZED': lambda : {
                                'FAILURE': 'red',
                                'SUCCESS': 'green'
                            }.get(data['build']['status'], 'grey')
                        }.get(data['build']['phase'], lambda : 'grey')(),
                        "title": {
                            "content": f"[Jenkins Job {data['build']['phase'].title()}] {data['display_name']}",
                            "tag": "plain_text"
                        }
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "fields": [
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**Name**：\n{data['display_name']}"
                                    }
                                },
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**URL**：\n{data['build']['full_url']}"
                                    }
                                },
                                {
                                    "is_short": False,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": data['build']['log']
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            requests.post(feishu_webhook, json=feishu_msg)
        else:
            print(f'Not job: {data["build"]["full_url"]}, phase: {data["build"]["phase"]}')


if __name__ == "__main__":
    web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", 8000))
