from .role import *
import collections
import hashlib
import datetime
from abc import ABC, abstractmethod


def gen_sign(appid: str, appkey: str, ts: int) -> str:
    sign_str = f"_appid={appid}&_appkey={appkey}&_ts={ts}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


class User(object):
    _username: str
    _password: str
    _roles: list[Role]

    def __init__(self, username: str, password: str, roles: list[Role]):
        self._username = username
        self._password = password
        self._roles = roles

    def username(self) -> str:
        return self._username

    def authenticate(self, password: str) -> bool:
        return self._password == password

    def authenticate_api(self, sign: str, ts: int) -> bool:
        # Convert Unix timestamp to datetime object
        then = datetime.datetime.fromtimestamp(ts)
        now = datetime.datetime.now()
        # Calculate the time difference
        diff = now - then
        # Check if the time difference is within 10 seconds
        if abs(diff.total_seconds()) > 10:
            return False
        expected = gen_sign(self._username, self._password, ts)
        return expected == sign

    def authorize(self, env: str, module: str, func: str, opcode: int) -> bool:
        for role in self._roles:
            # Pass at least one role is authorized
            if role.authorize(env, module, func, opcode):
                return True
        return False

    def __repr__(self):
        return f"User(username={self._username}, password={self._password}, roles={self._roles})"


class BaseExternalUsers(ABC):
    """
    Base abstract class for implementing external or remote users manager.

    You can define a subclass and cache remote users in memory for high performance.
    """

    @abstractmethod
    def get(self, username: str) -> User:
        """
        Get a full User object by username for auth.
        """
        pass


class Users(object):
    _users: collections.OrderedDict[str, User]
    _external_users: BaseExternalUsers

    def __init__(self, external_users: BaseExternalUsers = None):
        self._users = collections.OrderedDict[str, User]()
        self._external_users = external_users

    def add(self, username: str, password: str, roles: list[Role]):
        """Add a local user."""
        self._users[username] = User(username, password, roles)

    def add_user(self, user: User):
        """Add a local user."""
        self._users[user._username] = user

    def get(self, username: str) -> User:
        """
        Firstly, find the user locally. If not found, then find from external users if provided.
        """
        user = self._users.get(username, None)
        if user:
            return user
        if self._external_users:
            return self._external_users.get(user)
        return None

    def authenticate(self, username: str, password: str) -> tuple[bool, User]:
        user = self.get(username)
        if user:
            return user.authenticate(password), user
        return False, None

    def authenticate_api(self, appid: str, sign: str, ts: int) -> tuple[bool, User]:
        user = self.get(appid)
        if user:
            return user.authenticate_api(sign, ts), user
        return False, None

    def authorize(
        self, username: str, env: str, module: str, func: str, opcode: int
    ) -> bool:
        user = self.get(username)
        if user:
            return user.authorize(env, module, func, opcode)
        return False

    def __repr__(self):
        out = ""
        for user in self._users.values():
            out += f"{user}\n"
        return out


# Test: python3 -m core.rbac.user
if __name__ == "__main__":
    anon = User("anon", "anonpw", [STAFF])
    print(anon)

    users = Users()
    users.add_user(anon)
    users.add("admin", "adminpw", [ADMIN])
    print(users)
    ts = int(datetime.datetime.now().timestamp())
    sign = gen_sign("appid", "appkey", ts)
    print(f"_appid=appid&_sign={sign}&_ts={ts}")
