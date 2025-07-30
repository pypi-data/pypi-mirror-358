# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2025 CONTACT Software GmbH
# https://www.contact-software.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import logging

from http import server
from typing import Optional

from oic import rndstr
from oic.oic import Client
from oic.oic.message import AuthorizationResponse, RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

logger = logging.getLogger(__name__)


class RPRequestHandler(server.BaseHTTPRequestHandler):
    def parse_auth_response(self) -> None:
        response = self.path[len("/callback?") :]  # noqa: E203
        logger.debug("Response: %s", response)

        aresp = self.server.client.parse_response(  # type: ignore
            AuthorizationResponse, info=response, sformat="urlencoded"
        )
        self.server.auth_code = aresp["code"]  # type: ignore
        self.server.auth_event.set()  # type: ignore

    # Override log_message to send access logs to our new logger.
    def log_message(self, format, *args):  # type: ignore
        logger.debug(format, *args)

    # Override log_error to send server errors to our new logger.
    def log_error(self, format, *args):  # type: ignore
        logger.error(format, *args)

    def do_GET(self) -> None:
        if self.path.startswith("/callback?"):
            logger.debug("Got callback GET.")
            self.parse_auth_response()

        # The tab is not closed automatically, we rely on the text instructions.
        content = b"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Complete</title>
        </head>
        <body>
            <h3>Authentication Complete</h3>
            <p>This window will close automatically. If it doesn't, you can close it manually.</p>
            <script>
                // Try multiple approaches to close the window.
                window.addEventListener('load', function() {
                    // First attempt
                    window.close();

                    // Second attempt - countdown and close.
                    let counter = 3;
                    const countdown = document.createElement('p');
                    document.body.appendChild(countdown);

                    const timer = setInterval(function() {
                        countdown.textContent = 'Closing in ' + counter + ' seconds...';
                        counter--;
                        if (counter < 0) {
                            clearInterval(timer);
                            window.close();
                        }
                    }, 1000);
                });
            </script>
        </body>
        </html>
        """

        self.send_response(200, "Authentication Complete")
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        if self.path.startswith("/callback"):
            logger.debug("Got callback POST.")
        self.send_response(200, "All good")
        self.end_headers()


class RPServer(threading.Thread):
    """
    Simple RP Service

    Fires up an HTTP Server on 127.0.0.1 to receive the authorization code.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self.port = 29398

        self.issuer = kwargs.pop("oidc_issuer")
        self.client_id = kwargs.pop("client_id")
        client_info = {
            "client_id": self.client_id,
            "client_secret": kwargs.pop("client_secret"),
        }
        self.client_registration = RegistrationResponse(**client_info)

        super().__init__(name="RP HTTPD", daemon=True)

        self.client = Client(client_id=self.client_id, client_authn_method=CLIENT_AUTHN_METHOD)
        provider_info = self.client.provider_config(self.issuer)
        self.client.handle_provider_config(provider_info, self.issuer)
        self.client.store_registration_info(self.client_registration)

        self.pkce_verifier = None
        self.addr = ("", self.port)
        self.hdlr = RPRequestHandler
        self.auth_event = threading.Event()

        self.srv = server.HTTPServer(self.addr, self.hdlr)
        self.srv.client = self.client  # type: ignore
        self.srv.timeout = 0.05  # Wakeup every 50ms
        self.srv.auth_code = None  # type: ignore
        self.srv.auth_event = self.auth_event  # type: ignore
        self.srv.auth_event.clear()  # type: ignore

        self._shutdown_requested = False

    def run(self) -> None:
        try:
            while not self._shutdown_requested:
                self.srv.handle_request()
        finally:
            # Proper cleanup
            if self.srv:
                self.srv.server_close()
                logger.debug("HTTP server closed.")

    def shutdown(self) -> None:
        """Shut down the server and thread"""
        logger.debug("Shutting down RPServer.")
        self._shutdown_requested = True

        # Wait for the thread to finish (with timeout).
        if self.is_alive():
            self.join(timeout=2.0)

        # Force server shutdown if still alive.
        if hasattr(self, "srv") and self.srv:
            try:
                self.srv.server_close()
                logger.debug("Server resources released")
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error during server cleanup: %s", e)

        logger.debug("RPServer shutdown complete.")

    def get_auth_url(
        self,
        session: Optional[dict] = None,
        extra_scopes: Optional[list] = None,
        login_hint: Optional[str] = None,
        use_pkce: bool = False,
    ) -> str:
        if session is None:
            session = {}

        session["state"] = rndstr()
        session["nonce"] = rndstr()
        args = {
            "client_id": self.client.client_id,
            "response_type": "code",
            "scope": ["openid"],
            "nonce": session["nonce"],
            "redirect_uri": [f"http://127.0.0.1:{self.port}/callback"],
            "state": session["state"],
        }
        if use_pkce:
            pkce_args, pkce_verifier = self.client.add_code_challenge()
            args.update(pkce_args)
            self.pkce_verifier = pkce_verifier

        if extra_scopes:
            args["scope"].extend(extra_scopes)
        if login_hint:
            args["login_hint"] = login_hint

        auth_req = self.client.construct_AuthorizationRequest(request_args=args)
        return str(auth_req.request(self.client.authorization_endpoint))
