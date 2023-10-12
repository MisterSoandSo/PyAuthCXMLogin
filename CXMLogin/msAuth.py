import json
import urllib.parse
from typing import Optional
import requests

URL_BASE = "https://login.live.com/oauth20_{}.srf"


def check_response(resp: requests.Response):
    try:
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(resp.text)
        raise e


def json_request(url: str, data: Optional[dict] = None, *, auth_token: Optional[str] = None) -> dict:
    req_headers = {"Accept": "application/json"}
    if auth_token is not None:
        req_headers["Authorization"] = f"Bearer {auth_token}"

    function_call_kwargs = {}
    meth = "post" if data is not None else "get"

    if data is not None:
        req_headers["Content-Type"] = "application/json"
        function_call_kwargs["data"] = json.dumps(data).encode()

    function_call_kwargs["headers"] = req_headers
    resp = getattr(requests, meth)(url, **function_call_kwargs)
    check_response(resp)
    return resp.json()


def get_from_json(resp: requests.Response, *items: str):
    return map(resp.json().__getitem__, items)


class Authentication:
    def __init__(self, client_id, client_secret, redirect_uri) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def query_microsoft_code(self):
        query = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        scope = "XboxLive.signin%20offline_access"
        return f"{URL_BASE.format('authorize')}?{urllib.parse.urlencode(query)}&scope={scope}"

    def query_token(self, *, code: Optional[str] = None, refresh_token: Optional[str] = None, grant_type: str):
        token_url_query = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type,
            "redirect_uri": self.redirect_uri
        }

        if code is not None:
            token_url_query["code"] = code
        elif refresh_token is not None:
            token_url_query["refresh_token"] = refresh_token
        else:
            raise Exception("Need either code or refresh_token")

        token_resp = requests.post(
            f"{URL_BASE.format('token')}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=urllib.parse.urlencode(token_url_query).encode()
        )
        check_response(token_resp)
        return get_from_json(token_resp, "access_token", "refresh_token")

    def reauth_token(self, *, refresh_token: str):
        return self.query_token(refresh_token=refresh_token, grant_type="refresh_token")

    def get_auth_token(self, msft_access_token):
        xbl_req_json = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={msft_access_token}"
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }
        xbl_resp = json_request("https://user.auth.xboxlive.com/user/authenticate", xbl_req_json)
        xbl_token = xbl_resp["Token"]
        xbl_userhash = xbl_resp["DisplayClaims"]["xui"][0]["uhs"]

        xsts_req_json = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [xbl_token]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }
        xsts_resp = json_request("https://xsts.auth.xboxlive.com/xsts/authorize", xsts_req_json)
        xsts_token = xsts_resp["Token"]
        xsts_userhash = xsts_resp["DisplayClaims"]["xui"][0]["uhs"]
        assert xbl_userhash == xsts_userhash

        mc_auth_req_json = {"identityToken": f"XBL3.0 x={xbl_userhash};{xsts_token}"}
        mc_auth_resp = json_request("https://api.minecraftservices.com/authentication/login_with_xbox", mc_auth_req_json)
        mc_access_token = mc_auth_resp["access_token"]

        mc_ownership_check_resp = json_request("https://api.minecraftservices.com/entitlements/mcstore",
                                              auth_token=mc_access_token)
        if not any(map(lambda item_name: item_name.endswith("minecraft"), map(lambda item: item["name"],
                                                                               mc_ownership_check_resp["items"]))):
            raise Exception("Account does not own Minecraft!")

        mc_profile = json_request("https://api.minecraftservices.com/minecraft/profile", auth_token=mc_access_token)
        mc_uuid = mc_profile["id"]
        mc_username = mc_profile["name"]

        return [mc_uuid, mc_username, mc_access_token]
