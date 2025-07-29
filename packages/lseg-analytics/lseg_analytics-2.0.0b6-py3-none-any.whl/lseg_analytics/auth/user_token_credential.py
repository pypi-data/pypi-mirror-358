import time
import webbrowser
from typing import Any, List, Optional

import pkce
import requests
from corehttp.credentials import AccessToken, TokenCredential
from requests_oauthlib import OAuth2Session

from ..exceptions import _ERROR_MESSAGE, AuthenticationError
from ._logger import logger
from .loopback_client import LoopbackClient

AUTH_GRANT_TYPE = "authorization_code"
RESPONSE_TYPE = "code"
RESPONSE_MODE = "query"
CODE_CHALLENGE_METHOD = "S256"


class UserTokenCredential(TokenCredential):
    def __init__(self, client_id: str, authority: str, redirect_uri: str, scopes: List[str]):
        self.client_id = client_id
        self.authority = authority if authority.startswith("https") else f"https://{authority}"
        self.redirect_uri = redirect_uri
        self.scope = " ".join(scopes)

    # get the access token
    def get_token(self, *scopes: str, claims: Optional[str] = None, **kwargs: Any) -> AccessToken:
        try:
            # create loopback listener
            logger.info("Create loopback listener")
            loopback_client = LoopbackClient.initialize(redirect_uri=self.redirect_uri)

            # update the local redirectUri with the loopback port added
            self.redirect_uri = loopback_client.redirect_uri

            # Get authorization request URL
            logger.info("Get authorization request URL")
            aaa = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
            authorization_url, state = aaa.authorization_url(f"{self.authority}/as/authorization.oauth2")
            logger.info("Create PKCE code verifier and challenge")
            code_verifier, code_challenge = pkce.generate_pkce_pair()
            authorization_url += f"&code_challenge={code_challenge}&code_challenge_method={CODE_CHALLENGE_METHOD}"

            logger.info("Invoking authorization_code grant type")
            # open browser to authorization URL
            webbrowser.open_new(authorization_url)

            # listen for auth code
            auth_code = loopback_client.listen_for_auth_code()

            # handle auth code token exchange
            request_data = {
                "grant_type": AUTH_GRANT_TYPE,
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "code_verifier": code_verifier,
                "code": auth_code,
            }

            token_url = f"{self.authority}/as/token.oauth2"
            logger.info(f"Getting access token using authorization_code grant type from {token_url}")

            response = requests.post(token_url, data=request_data)
            data = response.json()
            if "access_token" in data:
                access_token = data["access_token"]
            else:
                msg = "Access token could not be retrieved"
                logger.fatal(msg)
                raise AuthenticationError(msg)
            expires_in = data["expires_in"] if "expires_in" in data else 0
            logger.info("Access token retrieved successfully")

            return AccessToken(token=access_token, expires_on=time.time() + expires_in)
        except AuthenticationError as auth_err:
            raise auth_err
        except Exception as e:
            logger.error(f"Failed to get access token. Error: {e}")
            raise AuthenticationError(_ERROR_MESSAGE.GET_TOKEN_FAILED.value)
