#!/usr/bin/env python

import os
import sys
import json
import base64
import hashlib
import urllib.parse
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import click
from click import pass_context, command, option, secho, echo
import requests
import logging

from nextcode.config import get_profile_config, get_default_profile, create_profile
from nextcode.exceptions import InvalidProfile, InvalidToken
from nextcode.client import get_api_key
from nextcodecli.utils import abort, dumps

log = logging.getLogger(__name__)

def legacy_login(username, password, realm, host, is_token):
    try:
        config = get_profile_config()
    except InvalidProfile as ex:
        secho(str(ex), fg="red")
        abort("Please create a profile with: nextcode profile add [name]")
    profile_name = get_default_profile()

    if username and password:
        if not is_token:
            echo("Authenticating from commandline parameters")
        host = host or config["root_url"]
        try:
            api_key = get_api_key(host, username, password, realm=realm)
        except InvalidToken as ex:
            abort(ex)
        if is_token:
            click.echo(api_key)
            return
        create_profile(profile_name, api_key=api_key, root_url=host)
        click.secho("Profile {} has been updated with api key".format(profile_name), bold=True)

    else:
        if host:
            root_url = "https://%s" % host
        else:
            root_url = config["root_url"]
        login_server = root_url + "/api-key-service"

        if login_server:
            echo("Launching login webpage ==> Please authenticate and then press continue.")
            click.launch(login_server)
            click.pause()
        else:
            click.secho(
                "No login server configured. Please aquire a refresh_token from "
                "somewhere manually.",
                fg='yellow',
            )

        # Note: readline must be imported for click.prompt() to accept long strings. Don't ask me why.
        import readline

        api_key = click.prompt("API Key", type=str)
        try:
            create_profile(profile_name, api_key=api_key)
        except InvalidProfile as ex:
            abort(ex)

# === PKCE Utilities ===
def generate_pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(64)).decode("utf-8").rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return verifier, challenge

# === Simple HTTP Server to Capture Redirect ===
class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = urllib.parse.parse_qs(parsed_path.query)
        self.server.auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h2>You may now return to your terminal.</h2></body></html>")

    def log_message(self, format, *args):
        if getattr(self.server, 'verbose_logging', False):
            super().log_message(format, *args)
        # Otherwise suppress HTTP server logs


def start_server(port, verbose=False):
    httpd = HTTPServer(("", port), CallbackHandler)
    httpd.verbose_logging = verbose
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


@command()
@click.argument('tier', type=click.Choice(['dev', 'stg', 'prd']), required=False)
@option('-u', '--username')
@option('-p', '--password')
@option('-r', '--realm', default='genedx-prd')
@option(
    '-h',
    '--host',
    default=None,
    help="Host override if not using profile, e.g. platform.wuxinextcodedev.com",
)
@option(
    '-t',
    '--token',
    'is_token',
    is_flag=True,
    help="Return refresh token instead of writing into current profile",
)
@option('-l', '--legacy', is_flag=True, help="Use legacy login")
@option('-v', '--verbose', is_flag=True, help="Enable verbose HTTP server logging for troubleshooting")
@pass_context
def cli(ctx, tier, username, password, realm, host, is_token, legacy, verbose):
    """
    Authenticate against keycloak.

    TIER: Optional environment tier (dev|stg|prd). Defaults to 'dev'.
    Ignored when using --legacy flag.

    LEGACY: Use legacy login.

    VERBOSE: Enable verbose HTTP server logging for troubleshooting.

    TOKEN: Return refresh token instead of writing into current profile.
    """
    try:
        config = get_profile_config()
    except InvalidProfile as ex:
        secho(str(ex), fg="red")
        abort("Please create a profile with: nextcode profile add [name]")
    profile_name = get_default_profile()

    if legacy:
        return legacy_login(username, password, realm, host, is_token)

    # Default to dev if no tier specified
    if tier is None:
        tier = 'dev'

    configs = {
        "dev":  ("https://auth.dev.engops.genedx.net", "genedx-dev"),
        "stg":  ("https://auth.stg.engops.genedx.net", "genedx-stg"),
        "prd":  ("https://auth.engops.genedx.net", "genedx"),
    }
    keycloak_url, realm = configs[tier]
    client_id = "gdb-api-key-service"
    redirect_uri = "http://localhost:8000/callback"
    port = 8000

    verifier, challenge = generate_pkce_pair()

    auth_url = (
        f"{keycloak_url}/realms/{realm}/protocol/openid-connect/auth"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope=openid&code_challenge={challenge}&code_challenge_method=S256"
    )

    click.secho("Waiting for browser login (Ctrl+C to cancel)...", fg="green")
    server = start_server(port, verbose)

    click.secho("Opening browser...", fg="green")
    webbrowser.open(auth_url)

    while not getattr(server, "auth_code", None):
        pass  # busy-wait

    code = server.auth_code
    server.shutdown()

    if not code:
        click.secho("Failed to retrieve code from callback", fg="red")
        exit(1)

    click.secho("Exchanging code for tokens...", fg="green")
    token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    tokens = response.json()

    click.echo(json.dumps(tokens, indent=2))
