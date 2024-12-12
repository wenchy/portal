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
