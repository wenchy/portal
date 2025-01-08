import collections
from core.auth import auth

# A pluggable N-level authentication module.
AUTHS = collections.OrderedDict(
    [
        # ("xx", {"handler": auth.xxx, "level": 4}),
        ("api", {"handler": auth.api, "level": 3}),
        ("basic", {"handler": auth.basic, "level": 2}),
        ("anonym", {"handler": auth.anonym, "level": 1}),
    ]
)
