import json
import logging
from typing import Optional, TypedDict, Literal, Callable
import requests
from websockets import Origin
from websockets.sync.client import connect
from urllib.parse import urlparse
from ..config import get_requestbin_config


server_url, requestbin_app, access_token = get_requestbin_config()

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {access_token}"})


class RequestbinUpdateData(TypedDict, total=False):
    is_data_base64_encoded: Optional[bool]
    js_payload_id: Optional[Literal[1, 2]]
    response_code: Optional[int]
    response_mime: Optional[str]
    response_body: Optional[str]
    response_cors_headers: Optional[bool]
    response_headers: Optional[dict[str, str]]


class RequestResponse:
    def __init__(self, data):
        self.id: int = data["id"]
        self.created_at: str = data["created_at"]
        self.url: str = data["url"]
        self.method: str = data["method"]
        self.body: str = data["body"]
        self.headers: dict[str, str] = data["headers"]

    def __str__(self):
        return f"RequestResponse(id={self.id}, created_at={self.created_at}, url={self.url}, method={self.method}, body={self.body}, headers={self.headers})"


class requestbin:
    def __init__(self, requestbin_id: int, logging_level=logging.WARN):
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging_level)
        self.requestbin_id = requestbin_id
        self.websocket = None

    def __enter__(self):
        self.websocket = connect(
            uri=f"{urlparse(server_url)._replace(scheme='wss').geturl()}/app/{requestbin_app}?protocol=7&client=js&version=8.4.0&flash=false",
            origin=Origin(server_url),
        )

        socket_id = json.loads(json.loads(self.websocket.recv())["data"])["socket_id"]

        response = session.post(
            url=f"{server_url}/api/broadcasting/auth",
            data={
                "socket_id": socket_id,
                "channel_name": f"private-requestbin.{self.requestbin_id}.events",
            },
            allow_redirects=False,
        )

        if response.status_code != 200:
            logging.error(
                f"Failed to authenticate socket: {response.status_code} - {response.text}"
            )
            exit(1)

        auth = response.json()["auth"]

        self.websocket.send(
            json.dumps(
                {
                    "event": "pusher:subscribe",
                    "data": {
                        "auth": auth,
                        "channel": f"private-requestbin.{self.requestbin_id}.events",
                    },
                }
            )
        )

        message = json.loads(self.websocket.recv())

        if (
            message.get("event") != "pusher_internal:subscription_succeeded"
            or message.get("channel")
            != f"private-requestbin.{self.requestbin_id}.events"
        ):
            logging.error(f"Failed to subscribe to channel: {message}")
            exit(1)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            self.websocket.close()

    def update(self, data: RequestbinUpdateData) -> None:
        response = session.patch(
            f"{server_url}/api/bin/{self.requestbin_id}",
            json=data,
            allow_redirects=False,
        )

        if response.status_code != 200:
            logging.error("Failed to update requestbin")
            exit(1)

    def recv_until(self, func: Callable[[RequestResponse], bool], timeout: int = None) -> Optional[RequestResponse]:
        if not self.websocket:
            return None

        while True:
            event = self.recv(timeout=timeout)

            if func(event):
                return event

    def recv(self, timeout: int = None) -> Optional[RequestResponse]:
        if not self.websocket:
            return None

        data = json.loads(
            json.loads(
                self.websocket.recv(
                    timeout=timeout,
                )
            )["data"]
        )["event"]

        return RequestResponse(data)
