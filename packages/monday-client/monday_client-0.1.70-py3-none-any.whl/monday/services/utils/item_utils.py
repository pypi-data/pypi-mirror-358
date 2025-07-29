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

"""Utility functions for safe item property access."""

from typing import Any, TypeVar

from monday.types.column import ColumnValue
from monday.types.item import Item

T = TypeVar('T')


def get_column_values(item: Item | dict[str, Any]) -> list[ColumnValue] | None:
    """
    Safely get column_values from an item.

    Args:
        item: The item to get column_values from.

    Returns:
        List of column values or None if not available.

    Example:
        >>> item = {'column_values': [{'id': 'status', 'text': 'Done'}]}
        >>> get_column_values(item)
        [{'id': 'status', 'text': 'Done'}]
        >>> get_column_values({'name': 'Item 1'})
        None
    """
    if hasattr(item, 'column_values'):
        return item.column_values

    if isinstance(item, dict):
        return item.get('column_values')

    return None


def get_item_property(item: Item | dict[str, Any], property_name: str, default: T | None = None) -> Any | T:
    """
    Safely get any property from an item.

    Args:
        item: The item to get the property from.
        property_name: Name of the property to get.
        default: Default value if property is not found.

    Returns:
        Property value or default.

    Example:
        >>> item = {'name': 'Item 1', 'id': '123'}
        >>> get_item_property(item, 'name')
        'Item 1'
        >>> get_item_property(item, 'nonexistent', default='default')
        'default'
    """
    if hasattr(item, property_name):
        return getattr(item, property_name)

    if isinstance(item, dict):
        return item.get(property_name, default)

    return default


def has_column_values(item: Item | dict[str, Any]) -> bool:
    """
    Check if an item has column_values.

    Args:
        item: The item to check.

    Returns:
        True if item has column_values, False otherwise.

    Example:
        >>> item = {'column_values': [{'id': 'status', 'text': 'Done'}]}
        >>> has_column_values(item)
        True
        >>> has_column_values({'name': 'Item 1'})
        False
    """
    column_values = get_column_values(item)
    return column_values is not None and len(column_values) > 0
