"""
A pluggable N-level authentication module ordered by priority.

More bigger the list index, then more higher the priority.
The auth module will authenticate from high to low priority until it passes.
"""

from core.auth import auth

AUTHS: list[auth.BaseAuth] = [
    auth.Anonym("anonym"),  # Anoymous
    auth.Basic("basic"),  # HTTP basic
    auth.API("api"),  # API token
    # more: auth.xxx
]
