from .role import *
import collections
import re


class User(object):
    def __init__(self, username: str, password: str, roles: list[Role]):
        self.username = username
        self.password = password
        self.roles = roles

    def authenticate(self, password: str) -> bool:
        return self.password == password

    def authorize(self, env: str, module: str, func: str, opcode: int) -> bool:
        for role in self.roles:
            # pass at least one role is authorized
            if role.authorize(env, module, func, opcode):
                return True
        return False

    def __repr__(self):
        return f"User(username={self.username}, password={self.password}, roles={self.roles})"


class Users(object):
    def __init__(self):
        self.users = collections.OrderedDict[str, User]()

    def add(self, username: str, password: str, roles: list[Role]):
        self.users[username] = User(username, password, roles)

    def add_user(self, user: User):
        self.users[user.username] = user

    def authenticate(self, username: str, password: str) -> bool:
        user = self.users.get(username, None)
        if user:
            return user.authenticate(password)
        return False

    def authorize(
        self, username: str, env: str, module: str, func: str, opcode: int
    ) -> bool:
        user = self.users.get(username, None)
        if user:
            return user.authorize(env, module, func, opcode)
        return False

    def __repr__(self):
        out = ""
        for user in self.users.values():
            out += f"{user}\n"
        return out


# Test
if __name__ == "__main__":
    anon = User("anon", "anonpw", [STAFF])
    print(anon)

    users = Users()
    users.add_user(anon)
    users.add("admin", "adminpw", [ADMIN])
    print(users)
