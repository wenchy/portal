class Context(object):
    """Represents a context submitted via a form.

    * ``uid: int``
    * ``opcode: int``
    * ``account_type: int``
    * ``zone_id: int``
    * ``env: dict``: value of config.ENVS
    * ``trace_id: int``
    * ``extras: dict``
    """

    uid: int
    opcode: int
    account_type: int
    zone_id: int
    env: dict
    trace_id: int
    extras: dict

    def __init__(
        self,
        uid: int,
        opcode: int,
        account_type: int,
        zone_id: int,
        env: dict,
        trace_id: int,
        extras: dict,
    ):
        self.uid = uid
        self.opcode = opcode
        self.account_type = account_type
        self.zone_id = zone_id
        self.env = env  # value of config.ENVS
        self.trace_id = trace_id
        self.extras = extras

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __repr__(self):
        return f"Context(uid:{self.uid},zone_id:{self.zone_id},trace_id:{self.trace_id})"

    def dump(self):
        return str(self.__dict__)


if __name__ == "__main__":
    ctx = Context(
        288300748311436289,
        1,
        1,
        {},
        {"username": "admin"},
        998300748311436289,
    )
    print(ctx)
    print(ctx.dump())
