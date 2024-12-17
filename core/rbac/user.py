from .role import *
import collections
import hashlib
import datetime


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


class Users(object):
    _users: collections.OrderedDict[str, User]

    def __init__(self):
        self._users = collections.OrderedDict[str, User]()

    def add(self, username: str, password: str, roles: list[Role]):
        self._users[username] = User(username, password, roles)

    def add_user(self, user: User):
        self._users[user._username] = user

    def get(self, username: str) -> User:
        return self._users.get(username, None)

    def authenticate(self, username: str, password: str) -> bool:
        user = self._users.get(username, None)
        if user:
            return user.authenticate(password)
        return False

    def authenticate_api(self, appid: str, sign: str, ts: int) -> bool:
        user = self._users.get(appid, None)
        if user:
            return user.authenticate_api(sign, ts)
        return False

    def authorize(
        self, username: str, env: str, module: str, func: str, opcode: int
    ) -> bool:
        user = self._users.get(username, None)
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
