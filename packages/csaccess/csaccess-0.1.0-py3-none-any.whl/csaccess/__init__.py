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

import argparse
import functools
import getpass
import importlib
import json
import logging
import os
import sys
import time
import urllib.request
import urllib.parse
import webbrowser

import boto3

from typing import Dict, Optional, Any

from csaccess.utils import mask_sensitive_data
from csaccess.rp import RPServer
from csaccess.constants import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


__all__ = ["get_ca_auth_token_programmatic", "get_ecr_auth_token_programmatic", "get_ca_pypi_url_programmatic"]


@functools.lru_cache(maxsize=1)
def get_issuer_config(oidc_issuer: str) -> Dict[str, Any]:
    """Retrieve and cache the OIDC issuer configuration."""
    logger.debug("get_issuer_config: %s", oidc_issuer)

    req = urllib.request.Request(
        f"{oidc_issuer}/.well-known/openid-configuration", headers={"Accept": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
        issuer_config: Dict[str, Any] = json.loads(data)

        if not issuer_config:
            raise ValueError("Response doesn't contain issuer config.")

        return issuer_config


def assume_aws_role_with_web_identity(
    oidc_access_token: str,
    role_arn: str,
    role_session_name: str,
    region: str,
    key_duration_seconds: int,
) -> Dict[str, Any]:
    """Request AWS STS credentials using the OIDC access token as a web identity."""
    logger.debug(
        "assume_aws_role_with_web_identity: %s, %s, %s, %s, %s",
        mask_sensitive_data(oidc_access_token),
        role_arn,
        role_session_name,
        region,
        key_duration_seconds,
    )

    sts_client = boto3.client("sts", region_name=region)
    sts_response = sts_client.assume_role_with_web_identity(
        RoleArn=role_arn,
        RoleSessionName=role_session_name,
        WebIdentityToken=oidc_access_token,
        DurationSeconds=key_duration_seconds,
    )
    credentials: Dict[str, Any] = sts_response.get("Credentials", {})
    if not all(k in credentials for k in ("AccessKeyId", "SecretAccessKey", "SessionToken")):
        raise ValueError("Incomplete AWS credentials received.")
    return credentials


def get_aws_client(service_name: str, credentials: Dict[str, Any], region: str) -> boto3.client:
    """Create a boto3 client with the given credentials."""
    logger.debug("get_issuer_config: %s, %s, %s", service_name, mask_sensitive_data(credentials), region)

    return boto3.client(
        service_name,
        region_name=region,
        aws_access_key_id=credentials.get("AccessKeyId"),
        aws_secret_access_key=credentials.get("SecretAccessKey"),
        aws_session_token=credentials.get("SessionToken"),
    )


def get_ecr_auth_token(credentials: Dict[str, Any], registry_id: str, region: str) -> str:
    """Retrieve the AWS ECR authentication token using temporary AWS credentials."""
    logger.debug("get_ecr_auth_token: %s, %s, %s", mask_sensitive_data(credentials), registry_id, region)

    ecr_client = get_aws_client("ecr", credentials, region)
    response = ecr_client.get_authorization_token(registryIds=[registry_id])
    auth_data = response.get("authorizationData", [])

    if not auth_data:
        raise ValueError("Failed to retrieve ECR authorization data.")

    auth_token: str = auth_data[0].get("authorizationToken", "")
    if not auth_token:
        raise ValueError("Failed to retrieve ECR authentication token.")

    return auth_token


def get_ca_auth_token(credentials: Dict[str, Any], domain: str, region: str) -> str:
    """Retrieve the AWS CodeArtifact authentication token using temporary AWS credentials."""
    logger.debug("get_ca_auth_token: %s, %s, %s", mask_sensitive_data(credentials), domain, region)

    ca_client = get_aws_client("codeartifact", credentials, region)
    response = ca_client.get_authorization_token(domain=domain)

    auth_token: str = response.get("authorizationToken", "")
    if not auth_token:
        raise ValueError("Failed to retrieve CodeArtifact authentication token.")

    return auth_token


def get_client_secret() -> str:
    """Get the client secret from environment or prompt user."""
    client_secret = os.environ.get("CS_AWS_OIDC_CLIENT_SECRET", "")
    if not client_secret:
        client_secret = getpass.getpass("Please enter your OIDC client secret: ")
    if not client_secret:
        raise ValueError("Client secret is required.")
    return client_secret


def get_client_access_token(oidc_issuer: str, client_id: str, client_secret: str) -> str:
    """Get the OIDC access token using static client credentials."""
    logger.debug(
        "get_client_access_token: %s, %s, %s",
        oidc_issuer,
        mask_sensitive_data(client_id),
        mask_sensitive_data(client_secret),
    )

    token_endpoint: str = get_issuer_config(oidc_issuer).get("token_endpoint", "")
    if not token_endpoint:
        raise ValueError("Token endpoint not found in issuer config.")

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    data = urllib.parse.urlencode(payload).encode("ascii")

    req = urllib.request.Request(
        token_endpoint,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        response_data = response.read()
        token_data = json.loads(response_data)

        access_token: str = token_data.get("access_token", "")
        if not access_token:
            raise ValueError("Response doesn't contain access_token.")

        return access_token


def get_user_access_token(oidc_issuer: str, client_id: str, client_secret: str) -> str:
    """Get the OIDC access token via user authentication flow."""
    logger.debug(
        "get_user_access_token: %s, %s, %s",
        oidc_issuer,
        mask_sensitive_data(client_id),
        mask_sensitive_data(client_secret),
    )

    rp = RPServer(
        oidc_issuer=oidc_issuer,
        client_id=client_id,
        client_secret=client_secret,
    )
    rp.start()

    # Session info is mutable dict, modified in RPServer.
    session_info: dict = {}
    auth_url = rp.get_auth_url(session_info, use_pkce=True)

    webbrowser.open(auth_url)
    while not rp.srv.auth_code:  # type: ignore
        time.sleep(0.1)

    request_args = {"code": rp.srv.auth_code, "code_verifier": rp.pkce_verifier}  # type: ignore

    resp = rp.client.do_access_token_request(
        request_args=request_args,
        state=session_info["state"],
        authn_method="client_secret_basic",
    )

    try:
        access_token: str = resp["access_token"]
    except KeyError as e:
        rp.shutdown()
        raise KeyError(f"OIDC response doesn't contain access token. Check your OIDC credentials. Error: {e}") from e

    return access_token


def get_access_token(oidc_issuer: str, client_id: str, client_secret: Optional[str], static_oidc: bool) -> str:
    """Get the appropriate OIDC access token based on args."""
    logger.debug(
        "get_access_token: %s, %s, %s, %s",
        oidc_issuer,
        mask_sensitive_data(client_id),
        mask_sensitive_data(client_secret),
        static_oidc,
    )

    if not client_secret:
        client_secret = get_client_secret()

    if static_oidc:
        return get_client_access_token(oidc_issuer, client_id, client_secret)
    else:
        return get_user_access_token(oidc_issuer, client_id, client_secret)


def get_aws_credentials(args: argparse.Namespace, access_token: str) -> Dict[str, Any]:
    """Get AWS credentials using the OIDC access token."""
    logger.debug("get_aws_credentials: %s, %s", mask_sensitive_data(args), mask_sensitive_data(access_token))

    return assume_aws_role_with_web_identity(
        access_token,
        args.aws_role_arn,
        args.aws_role_session_name,
        args.aws_region,
        args.aws_key_duration,
    )


def action_ecr_auth_token(args: argparse.Namespace) -> str:
    """Action to retrieve an ECR auth token."""
    logger.debug("action_ecr_auth_token: %s", mask_sensitive_data(args))

    access_token = get_access_token(args.oidc_issuer, args.client_id, "", args.static_oidc)
    credentials = get_aws_credentials(args, access_token)
    auth_token = get_ecr_auth_token(credentials, args.aws_tenant_id, args.aws_region)

    if not args.quiet:
        print("\033[1;32mAuthentication successful.\033[0m You can now proceed with docker commands:")
        print()
        print(
            f"echo '{auth_token}' | base64 -d | cut -d: -f2 | docker login --username AWS --password-stdin "
            f"{args.aws_tenant_id}.dkr.ecr.{args.aws_region}.amazonaws.com"
        )
        print(
            f"docker pull {args.aws_tenant_id}.dkr.ecr.{args.aws_region}.amazonaws.com/cs-central1-elements_platform:16.0.1"
        )
        print()
        print("Use --quiet option to suppress this message and only get the token.")
    else:
        # In quiet mode, just print the auth token (for scripting).
        print(auth_token)

    return auth_token


def action_ca_auth_token(args: argparse.Namespace) -> str:
    """Action to retrieve a CodeArtifact auth token."""
    logger.debug("action_ca_auth_token: %s", mask_sensitive_data(args))

    access_token = get_access_token(args.oidc_issuer, args.client_id, "", args.static_oidc)
    credentials = get_aws_credentials(args, access_token)
    ca_auth_token = get_ca_auth_token(credentials, args.aws_domain, args.aws_region)

    # Only print token if the method is called directly from cli.
    if args.action == "ca-auth-token":
        print(ca_auth_token)

    return ca_auth_token


def action_ca_pypi_url(args: argparse.Namespace) -> str:
    """
    Action to generate and display a PyPI URL in CodeArtifact.
    This URL should be amended with specific repo version and interface, e.g. /16.0/simple/.
    """
    logger.debug("action_ca_pypi_url: %s", mask_sensitive_data(args))

    ca_auth_token = action_ca_auth_token(args)
    domain_owner = args.aws_role_arn.split(":")[4]
    ca_pypi_url = (
        f"https://aws:{ca_auth_token}@"
        f"{args.aws_domain}-{domain_owner}"
        f".d.codeartifact.{args.aws_region}.amazonaws.com/pypi"
    )

    if not args.quiet:
        print("\033[1;32mAuthentication successful.\033[0m You can now use the following registry URL:")
        print(ca_pypi_url)
        print("For example, run:")
        print(f"pip install -i {ca_pypi_url}/16.0/simple cs.platform")
        print()
        print("Use --quiet option to suppress this message and only get the token.")
    else:
        # In quiet mode, just print the URL (for scripting).
        print(ca_pypi_url)

    return ca_pypi_url


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="csaccess",
        description="Provides access to CONTACT artifact storage.",
    )
    parser.add_argument(
        "action",
        choices=["ca-pypi-url", "ca-auth-token", "ecr-auth-token"],
        default="ca-pypi-url",
        nargs="?",
        help="Action to perform.",
    )
    parser.add_argument(
        "--static-oidc",
        action="store_true",
        default=False,
        help="Use static OIDC credentials.",
    )
    parser.add_argument("--aws-domain", default=DEFAULT_CONFIG["AWS_DOMAIN"], help="AWS domain name.")
    parser.add_argument(
        "--aws-key-duration",
        type=int,
        default=DEFAULT_CONFIG["AWS_KEY_DURATION"],
        help="AWS key duration in seconds.",
    )
    parser.add_argument(
        "--aws-region",
        default=DEFAULT_CONFIG["AWS_REGION"],
        help="AWS region name.",
    )
    parser.add_argument(
        "--aws-tenant-id",
        default=DEFAULT_CONFIG["AWS_TENANT_ID"],
        help="AWS tenant ID.",
    )
    parser.add_argument(
        "--aws-role-arn",
        default=DEFAULT_CONFIG["AWS_ROLE_ARN"],
        help="AWS role ARN for CodeArtifact and ECR access.",
    )
    parser.add_argument(
        "--aws-role-session-name",
        default=DEFAULT_CONFIG["AWS_ROLE_SESSION_NAME"],
        help="AWS STS role session name.",
    )
    parser.add_argument(
        "--oidc-issuer",
        default=DEFAULT_CONFIG["OIDC_ISSUER"],
        help="OIDC issuer URL for authentication.",
    )
    parser.add_argument(
        "--client-id",
        default=DEFAULT_CONFIG["OIDC_CLIENT_ID"],
        help="OIDC client ID for authentication.",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", default=False, help="Only output the result without additional text."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        default=False,
        action="store_true",
        help="Be verbose.",
    )
    parser.add_argument(
        "--version",
        default=False,
        action="store_true",
        help="Print current package version and exit.",
    )
    args = parser.parse_args()

    if args.version:
        print(f"csaccess version {importlib.metadata.version('csaccess')}")
        sys.exit(0)

    logging.basicConfig(
        format="[%(levelname)-8s] [%(name)s] [%(module)s] %(message)s",
        stream=sys.stderr,
        level=(logging.DEBUG if args.verbose else logging.INFO),
    )

    # Only log messages of level WARNING, ERROR, and CRITICAL from botocore lib.
    # INFO and DEBUG messages will be suppressed.
    logging.getLogger("botocore").setLevel(logging.WARNING)

    return args


def get_ca_auth_token_programmatic(
    oidc_issuer: str = DEFAULT_CONFIG["OIDC_ISSUER"],
    client_id: str = DEFAULT_CONFIG["OIDC_CLIENT_ID"],
    client_secret: Optional[str] = None,
    aws_domain: str = DEFAULT_CONFIG["AWS_DOMAIN"],
    aws_region: str = DEFAULT_CONFIG["AWS_REGION"],
    aws_role_arn: str = DEFAULT_CONFIG["AWS_ROLE_ARN"],
    aws_role_session_name: str = DEFAULT_CONFIG["AWS_ROLE_SESSION_NAME"],
    aws_key_duration: int = DEFAULT_CONFIG["AWS_KEY_DURATION"],
    static_oidc: bool = False,
) -> str:
    """
    Programmatically retrieve an AWS CodeArtifact authentication token.

    Args:
        oidc_issuer: OIDC issuer URL. Defaults to DEFAULT_CONFIG.
        client_id: OIDC client ID. Defaults to DEFAULT_CONFIG.
        client_secret: OIDC client secret. If None, tries CS_AWS_OIDC_CLIENT_SECRET env var
                       and interactive prompt. If not found, raises ValueError.
        aws_domain: AWS CodeArtifact domain name. Defaults to DEFAULT_CONFIG.
        aws_region: AWS region. Defaults to DEFAULT_CONFIG.
        aws_role_arn: AWS IAM Role ARN for OIDC federation. Defaults to DEFAULT_CONFIG.
        aws_role_session_name: AWS STS role session name. Defaults to DEFAULT_CONFIG.
        aws_key_duration: AWS temporary key duration in seconds. Defaults to DEFAULT_CONFIG.
        static_oidc: If True, uses client_credentials flow (requires client_secret).
                     If False, uses user authentication flow (opens browser).

    Returns:
        The CodeArtifact authentication token.
    """
    cli_args = argparse.Namespace(
        oidc_issuer=oidc_issuer,
        client_id=client_id,
        aws_domain=aws_domain,
        aws_region=aws_region,
        aws_role_arn=aws_role_arn,
        aws_role_session_name=aws_role_session_name,
        aws_key_duration=aws_key_duration,
        static_oidc=static_oidc,
        quiet=True,
        verbose=False,
        action="ca-auth-token",
    )

    access_token = get_access_token(oidc_issuer, client_id, client_secret, static_oidc)
    credentials = get_aws_credentials(cli_args, access_token)
    ca_auth_token = get_ca_auth_token(credentials, cli_args.aws_domain, cli_args.aws_region)

    return ca_auth_token


def get_ecr_auth_token_programmatic(
    oidc_issuer: str = DEFAULT_CONFIG["OIDC_ISSUER"],
    client_id: str = DEFAULT_CONFIG["OIDC_CLIENT_ID"],
    client_secret: Optional[str] = None,
    aws_tenant_id: str = DEFAULT_CONFIG["AWS_TENANT_ID"],
    aws_region: str = DEFAULT_CONFIG["AWS_REGION"],
    aws_role_arn: str = DEFAULT_CONFIG["AWS_ROLE_ARN"],
    aws_role_session_name: str = DEFAULT_CONFIG["AWS_ROLE_SESSION_NAME"],
    aws_key_duration: int = DEFAULT_CONFIG["AWS_KEY_DURATION"],
    static_oidc: bool = False,
) -> str:
    """
    Programmatically retrieve an AWS ECR authentication token.

    Args:
        oidc_issuer: OIDC issuer URL. Defaults to DEFAULT_CONFIG.
        client_id: OIDC client ID. Defaults to DEFAULT_CONFIG.
        client_secret: OIDC client secret. If None, tries CS_AWS_OIDC_CLIENT_SECRET env var
                       and interactive prompt. If not found, raises ValueError.
        aws_tenant_id: AWS ECR tenant ID. Defaults to DEFAULT_CONFIG.
        aws_region: AWS region. Defaults to DEFAULT_CONFIG.
        aws_role_arn: AWS IAM Role ARN for OIDC federation. Defaults to DEFAULT_CONFIG.
        aws_role_session_name: AWS STS role session name. Defaults to DEFAULT_CONFIG.
        aws_key_duration: AWS temporary key duration in seconds. Defaults to DEFAULT_CONFIG.
        static_oidc: If True, uses client_credentials flow (requires client_secret).
                     If False, uses user authentication flow (opens browser).

    Returns:
        The ECR authentication token.
    """
    cli_args = argparse.Namespace(
        oidc_issuer=oidc_issuer,
        client_id=client_id,
        aws_tenant_id=aws_tenant_id,
        aws_region=aws_region,
        aws_role_arn=aws_role_arn,
        aws_role_session_name=aws_role_session_name,
        aws_key_duration=aws_key_duration,
        static_oidc=static_oidc,
        quiet=True,
        verbose=False,
        action="ecr-auth-token",
    )

    access_token = get_access_token(oidc_issuer, client_id, client_secret, static_oidc)
    credentials = get_aws_credentials(cli_args, access_token)
    ecr_auth_token = get_ecr_auth_token(credentials, cli_args.aws_tenant_id, cli_args.aws_region)

    return ecr_auth_token


def get_ca_pypi_url_programmatic(
    oidc_issuer: str = DEFAULT_CONFIG["OIDC_ISSUER"],
    client_id: str = DEFAULT_CONFIG["OIDC_CLIENT_ID"],
    client_secret: Optional[str] = None,
    aws_domain: str = DEFAULT_CONFIG["AWS_DOMAIN"],
    aws_region: str = DEFAULT_CONFIG["AWS_REGION"],
    aws_role_arn: str = DEFAULT_CONFIG["AWS_ROLE_ARN"],
    aws_role_session_name: str = DEFAULT_CONFIG["AWS_ROLE_SESSION_NAME"],
    aws_key_duration: int = DEFAULT_CONFIG["AWS_KEY_DURATION"],
    static_oidc: bool = False,
) -> str:
    """
    Programmatically retrieve an AWS CodeArtifact PyPI URL. This URL should be amended with
    specific repository name and interface, for example /16.0/simple/.

    Args:
        oidc_issuer: OIDC issuer URL. Defaults to DEFAULT_CONFIG.
        client_id: OIDC client ID. Defaults to DEFAULT_CONFIG.
        client_secret: OIDC client secret. If None, tries CS_AWS_OIDC_CLIENT_SECRET env var
                       and interactive prompt. If not found, raises ValueError.
        aws_domain: AWS CodeArtifact domain name. Defaults to DEFAULT_CONFIG.
        aws_region: AWS region. Defaults to DEFAULT_CONFIG.
        aws_role_arn: AWS IAM Role ARN for OIDC federation. Defaults to DEFAULT_CONFIG.
        aws_role_session_name: AWS STS role session name. Defaults to DEFAULT_CONFIG.
        aws_key_duration: AWS temporary key duration in seconds. Defaults to DEFAULT_CONFIG.
        static_oidc: If True, uses client_credentials flow (requires client_secret).
                     If False, uses user authentication flow (opens browser).

    Returns:
        The CodeArtifact PyPI URL.
    """
    ca_auth_token = get_ca_auth_token_programmatic(
        oidc_issuer=oidc_issuer,
        client_id=client_id,
        client_secret=client_secret,
        aws_domain=aws_domain,
        aws_region=aws_region,
        aws_role_arn=aws_role_arn,
        aws_role_session_name=aws_role_session_name,
        aws_key_duration=aws_key_duration,
        static_oidc=static_oidc,
    )

    domain_owner = aws_role_arn.split(":")[4]
    ca_pypi_url = (
        f"https://aws:{ca_auth_token}@{aws_domain}-{domain_owner}.d.codeartifact.{aws_region}.amazonaws.com/pypi"
    )
    return ca_pypi_url


def main() -> None:
    """Main entry point."""
    interface = {
        "ca-pypi-url": action_ca_pypi_url,
        "ca-auth-token": action_ca_auth_token,
        "ecr-auth-token": action_ecr_auth_token,
    }

    args = parse_arguments()
    interface[args.action](args)


if __name__ == "__main__":
    main()
