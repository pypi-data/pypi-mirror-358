"""
Core components for Tamar Model Client

This package contains shared components used by both sync and async clients.
"""

from .utils import (
    is_effective_value,
    serialize_value,
    remove_none_from_dict,
    generate_request_id,
    set_request_id,
    get_request_id
)

from .logging_setup import (
    setup_logger,
    RequestIdFilter,
    MAX_MESSAGE_LENGTH
)

__all__ = [
    # Utils
    'is_effective_value',
    'serialize_value',
    'remove_none_from_dict',
    'generate_request_id',
    'set_request_id',
    'get_request_id',
    # Logging
    'setup_logger',
    'RequestIdFilter',
    'MAX_MESSAGE_LENGTH',
]