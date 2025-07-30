# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2025 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
Default constants for CS Access module.
"""

import os
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    # AWS Constants
    "AWS_DOMAIN": "contact",
    "AWS_KEY_DURATION": 43200,
    "AWS_REGION": "eu-central-1",
    "AWS_TENANT_ID": "373369985286",
    "AWS_ROLE_ARN": "arn:aws:iam::373369985286:role/cs-central1-codeartifact-ecr-read-role",
    "AWS_ROLE_SESSION_NAME": "CodeArtifactSession",
    # OIDC Constants
    "OIDC_ISSUER": "https://login.contact-cloud.com/realms/contact",
    "OIDC_CLIENT_ID": "central1-auth-oidc-read",
    # Environment Variable Names
    "ENV_CLIENT_SECRET": "CS_AWS_OIDC_CLIENT_SECRET",
}


def get_client_secret() -> str:
    """Get the client secret from environment variable."""
    client_secret = os.environ.get(DEFAULT_CONFIG["ENV_CLIENT_SECRET"], "")
    if not client_secret:
        raise ValueError(f"Environment variable {DEFAULT_CONFIG['ENV_CLIENT_SECRET']} is required.")
    return client_secret
