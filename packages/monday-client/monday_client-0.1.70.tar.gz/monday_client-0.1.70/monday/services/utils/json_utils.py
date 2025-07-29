# This file is part of monday-client.
#
# Copyright (C) 2024 Leet Cyber Security <https://leetcybersecurity.com/>
#
# monday-client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# monday-client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with monday-client. If not, see <https://www.gnu.org/licenses/>.

"""Utility functions for safe JSON handling with proper type annotations."""

import json
import logging
from typing import Any, TypeVar

logger: logging.Logger = logging.getLogger(__name__)

T = TypeVar('T')


def safe_json_loads(data: str | dict[str, Any] | None, default: T | None = None) -> dict[str, Any] | T:
    """
    Safely parse JSON data with proper type handling.

    Args:
        data: The data to parse. Can be a JSON string, dict, or None.
        default: Default value to return if parsing fails.

    Returns:
        Parsed dictionary or default value.

    Example:
        >>> safe_json_loads('{"key": "value"}')
        {'key': 'value'}
        >>> safe_json_loads({'key': 'value'})
        {'key': 'value'}
        >>> safe_json_loads(None, default={})
        {}
    """
    if data is None:
        return default if default is not None else {}

    if isinstance(data, dict):
        return data

    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.warning('Failed to parse JSON string: %s', e)
            return default if default is not None else {}

    logger.warning('Unexpected data type for JSON parsing: %s', type(data))
    return default if default is not None else {}


def safe_json_dumps(data: Any, default: str = '{}') -> str:
    """
    Safely serialize data to JSON string.

    Args:
        data: The data to serialize.
        default: Default string to return if serialization fails.

    Returns:
        JSON string or default value.

    Example:
        >>> safe_json_dumps({'key': 'value'})
        '{"key": "value"}'
        >>> safe_json_dumps(None)
        '{}'
    """
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        logger.warning('Failed to serialize data to JSON: %s', e)
        return default
