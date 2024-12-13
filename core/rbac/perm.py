import re


class Perm(object):
    """
    A class to represent permissions for a specific environment, module, function, and opcodes.

    Attributes:
        env (str): The environment name.
        module (str): The module name.
        func (str): The function name.
        opcodes (list[int | tuple]): A list of opcodes or ranges of opcodes.
    """

    def __init__(
        self,
        env: str,
        module: str,
        func: str,
        opcodes: list[int | tuple],
    ):
        self.env = env
        self.module = module
        self.func = func
        self.opcodes = opcodes

    def check(self, env: str, module: str, func: str, opcode: int) -> bool:
        if not re.match(self.env, env):
            return False
        elif not re.match(self.module, module):
            return False
        elif not re.match(self.func, func):
            return False
        else:
            # Check if opcode is in the list of opcodes
            for item in self.opcodes:
                if isinstance(item, int):
                    return opcode == item
                elif isinstance(item, tuple) and len(item) == 2:
                    begin, end = item
                    return begin <= opcode < end
                else:
                    raise Exception(f"illegal opcode item: {item}")

    def __repr__(self):
        return (
            f"Perm(env={self.env}, module={self.module}, func={self.func}, "
            f"opcodes={self.opcodes})"
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
