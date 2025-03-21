from urllib.request import Request, urlopen
import json

class BungieConnector:
    def __init__(self, x_api_key: str) -> None:
        self.__request_header = {"X-API-KEY": x_api_key}

    def get_url_request(self, path: str, method: str | None=None):
        req = Request(path, headers=self.__request_header, method=method)
        with urlopen(req) as response:
            json_out = json.loads(response.read())
        if json_out:
            return json_out["Response"]
        
# def main():
#     conn = BungieConnector("6250b4fbc6044931b45897c8109d692e")
#     conn.get_url_request("https://www.bungie.net/Platform/User/GetMembershipsById/4611686018441248186/1/")

# if __name__ == "__main__":
#     main()