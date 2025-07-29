import json
import logging
import requests
from websockets import Origin
from websockets.sync.client import connect
from urllib.parse import urlparse
from ..config import get_requestbin_config


server_url, requestbin_app, access_token = get_requestbin_config()


class requestbin:
    def __init__(self, requestbin_id: int, logging_level=logging.WARN):
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging_level)
        self.requestbin_id = requestbin_id
        self.websocket = None

    def __enter__(self):
        self.websocket = connect(uri=f"wss://{urlparse(server_url)._replace(scheme='wss').geturl()}/app/{requestbin_app}?protocol=7&client=js&version=8.4.0&flash=false",
                                 origin=Origin(server_url))

        socket_id = json.loads(json.loads(self.websocket.recv())['data'])['socket_id']

        response = requests.post(f"{server_url}/api/broadcasting/auth",
                                 data={"socket_id": socket_id, "channel_name": f"private-requestbin.{self.requestbin_id}.events"},
                                 headers={"Authorization": f"Bearer {access_token}"},
                                 allow_redirects=False)

        if response.status_code != 200:
            logging.error(f"Failed to authenticate socket: {response.status_code} - {response.text}")
            exit(1)

        auth = response.json()['auth']

        self.websocket.send(json.dumps({
            "event": "pusher:subscribe",
            "data": {"auth": auth, "channel": f"private-requestbin.{self.requestbin_id}.events"}
        }))

        message = json.loads(self.websocket.recv())

        if message.get("event") is not "pusher_internal:subscription_succeeded" or message.get("channel") is not f"private-requestbin.{self.requestbin_id}.events":
            logging.error(f"Failed to subscribe to channel: {message}")
            exit(1)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            self.websocket.close()

    def recv(self, timeout: int = None):
        if self.websocket:
            data = json.loads(json.loads(self.websocket.recv(timeout=timeout, ))['data'])['event']

            class RequestResponse:
                def __init__(self, data):
                    self.id = data['id']
                    self.created_at = data['created_at']
                    self.url = data['url']
                    self.method = data['method']
                    self.body = data['body']
                    self.headers = data['headers']

                def __str__(self):
                    return f"RequestResponse(id={self.id}, created_at={self.created_at}, url={self.url}, method={self.method}, body={self.body}, headers={self.headers})"

            return RequestResponse(data)
        return None
