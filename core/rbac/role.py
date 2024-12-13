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


_WITHOUT_ADMIN_MODULE_PATTERN = r"^(?!admin\.).*"
_WITHOUT_PROD_ENV_PATTERN = r"^(?!prod$).+$"

# role "guest"
GUEST = Role(
    "guest",
    [
        Perm(
            env=_WITHOUT_PROD_ENV_PATTERN,
            module=_WITHOUT_ADMIN_MODULE_PATTERN,
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
            env=_WITHOUT_PROD_ENV_PATTERN,
            module=_WITHOUT_ADMIN_MODULE_PATTERN,
            func=r".*",
            opcodes=[opcode.ALL],
        ),
        Perm(
            env="prod",  # only "prod"
            module=_WITHOUT_ADMIN_MODULE_PATTERN,
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
