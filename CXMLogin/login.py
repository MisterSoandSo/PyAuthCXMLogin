from .webdriver import Webdriver
from .msAuth import Authentication
import getpass
import os.path
import uuid
import configparser

# Configuration
config = configparser.ConfigParser()
config_file = 'config.ini'
config.read(config_file)
client_id = config.get("dev", "client_id")
client_secret = config.get("dev", "client_secret")
redirect_uri = config.get("dev", "redirect_uri")

client_token_file = "mc_client_token.txt"
save_file = "msft_refresh_token.txt"


class Login:
    def __init__(self, email=None, password=None):
        self.auth_token = None
        self.email = email
        self.password = password

        self.msft_access_token = None
        self.msft_refresh_token = None

        self.msftAuth = Authentication(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )

    def get_status(self):
        return self.auth_token is not None

    def get_uuid(self):
        if self.auth_token is not None:
            return self.auth_token[0]

    def get_username(self):
        if self.auth_token is not None:
            return self.auth_token[1]

    def get_token(self):
        if self.auth_token is not None:
            return self.auth_token

    def check_email(self):
        if self.email is None or self.password is None:
            self.email = input("Input Email: ")
            self.password = getpass.getpass("Input Password: ")

    def authenticate(self):
        # Microsoft Authentication Scheme
        if not os.path.exists(save_file):
            self.check_email()
            print(f"Tokens not detected ... Logging in with {self.email}")
            query_url = self.msftAuth.query_microsoft_code()
            browser = Webdriver(
                email=self.email,
                password=self.password
            )
            browser._get_url(query_url)
            mCode = browser._non_2FA_login(redirect=redirect_uri).split('?')[1][5:]
            self.msft_access_token, self.msft_refresh_token = self.msftAuth.query_token(code=mCode, grant_type="authorization_code")
            with open(save_file, "w+") as f:
                f.write(self.msft_refresh_token)
        else:
            print("Tokens detected ...")
            msft_refresh_token = open(save_file, "r").read()
            self.msft_access_token, self.msft_refresh_token = self.msftAuth.reauth_token(refresh_token=msft_refresh_token)
            with open(save_file, "w+") as f:
                f.write(self.msft_refresh_token)

        if not os.path.exists(client_token_file):
            client_token = uuid.uuid4().hex
            with open(client_token_file, "w+") as f:
                f.write(client_token)
        else:
            client_token = open(client_token_file, "r").read()

        self.auth_token = self.msftAuth.get_auth_token(self.msft_access_token)
        self.auth_token.append(client_token)
