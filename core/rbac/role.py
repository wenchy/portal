from .perm import Perm
from . import opcode


class Role(object):
    def __init__(self, name: str, perms: list[Perm]):
        self.name = name
        self.perms = perms

    def authorize(self, env: str, module: str, func: str, opcode: int) -> bool:
        for perm in self.perms:
            # pass at least one perm is authorized
            if perm.check(env, module, func, opcode):
                return True
        return False

    def __repr__(self):
        return f"Role(name={self.name}, perms={self.perms})"


# role "guest"
GUEST = Role(
    "guest",
    [
        Perm(
            env=r".*",  # except "prod"
            module=r".*",
            func=r".*",
            opcodes=[opcode.READ],
        ),
    ],
)

# role "staff"
STAFF = Role(
    "staff",
    [
        Perm(
            env=r"^(?!prod$).+$",  # except "prod"
            module=r".*",
            func=r".*",
            opcodes=[opcode.ALL],
        ),
        Perm(
            env="prod",  # only "prod"
            module=r".*",
            func=r".*",
            opcodes=[opcode.READ],
        ),
    ],
)

# role "admin"
ADMIN = Role(
    "admin",
    [
        Perm(
            env=r".*",
            module=r".*",
            func=r".*",
            opcodes=[opcode.ALL],
        ),
    ],
)

# Test
if __name__ == "__main__":
    print(STAFF)
    print(ADMIN)
