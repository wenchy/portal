import re


class Perm(object):
    """
    A class to represent permissions for a specific environment, module, function, and opcodes.
    """

    _env: str  # The environment name.
    _module: str  # The module name.
    _func: str  # The function name.
    _opcodes: list[int | tuple[int, int]]  # A list of opcodes or ranges of opcodes.

    def __init__(
        self,
        env: str,
        module: str,
        func: str,
        opcodes: list[int | tuple[int, int]],
    ):
        self._env = env
        self._module = module
        self._func = func
        self._opcodes = opcodes

    def check(self, env: str, module: str, func: str, opcode: int) -> bool:
        if not re.match(self._env, env):
            return False
        elif not re.match(self._module, module):
            return False
        elif not re.match(self._func, func):
            return False
        else:
            # Check if opcode is in the list of opcodes
            for item in self._opcodes:
                if isinstance(item, int):
                    if opcode == item:
                        return True
                elif isinstance(item, tuple) and len(item) == 2:
                    begin, end = item
                    if begin <= opcode < end:
                        return True
                else:
                    raise Exception(f"illegal opcode item: {item}")
            return False

    def __repr__(self):
        return (
            f"Perm(env={self._env}, module={self._module}, func={self._func}, "
            f"opcodes={self._opcodes})"
        )


# Test
if __name__ == "__main__":
    perm = Perm(
        env="dev",
        module="player",
        func="create",
        opcodes=[1, 2, (3, 5)],
    )
    print(perm)
