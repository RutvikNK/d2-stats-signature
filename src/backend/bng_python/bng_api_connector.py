from urllib.request import Request, urlopen
import json

class BungieConnector:
    def __init__(self, x_api_key: str) -> None:
        self.__request_header = {"X-API-KEY": x_api_key}

    def get_url_request(self, path):
        req = Request(path, headers=self.__request_header)
        with urlopen(req) as response:
            json_out = json.loads(response.read())
        if json_out:
            return json_out["Response"]
