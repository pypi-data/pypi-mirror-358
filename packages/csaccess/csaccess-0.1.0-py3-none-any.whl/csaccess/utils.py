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

from typing import Any


def mask_sensitive_data(data: Any, param_name: str = "", show_chars: int = 3) -> Any:
    """
    Create a copy of the data with sensitive information masked.

    Args:
        data: The data to be masked (dictionary, string, list, or None)
        param_name: Optional name of the parameter (for context-aware masking)
        show_chars: Number of characters to show before masking (0 for complete masking)

    Returns:
        Masked version of the input data
    """
    if data is None:
        return None

    # Handle dictionary case (recursively).
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Recursively mask nested values, passing the key name as context.
            result[key] = mask_sensitive_data(value, key)
        return result

    # Handle list case (recursively).
    if isinstance(data, list):
        return [mask_sensitive_data(item, param_name) for item in data]

    # Handle string case.
    if isinstance(data, str):
        # Check if the parameter name or string content suggests sensitive data.
        is_sensitive = param_name and any(
            sensitive in param_name.lower() for sensitive in ["password", "token", "secret", "key", "auth"]
        )

        # If the string itself contains obvious patterns, consider it sensitive.
        if not is_sensitive and len(data) > 20:
            # Check for patterns that suggest tokens or keys.
            token_patterns = ["ey", "sk_", "ak_", "pk_", "key-", "sess-"]
            is_sensitive = any(data.startswith(pattern) for pattern in token_patterns)

        if is_sensitive:
            if len(data) <= show_chars or show_chars <= 0:
                return "***MASKED***"
            else:
                return data[:show_chars] + "***MASKED***"

        return data

    # For other types (int, bool, etc.), just return as is.
    return data
