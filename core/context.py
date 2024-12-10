class Context(object):
    """
    Fields existed in context:
        - account_type: int
        - uid: int
        - zone_id: int
        - env: object
        - trace_id: int
        - extras: dict
    """

    account_type: int
    uid: int
    zone_id: int
    env: object
    trace_id: int
    extras: dict

    def __init__(
        self,
        account_type: int,
        uid: int,
        zone_id: int,
        env: object,
        trace_id: int,
        extras: dict,
    ):
        self.account_type = account_type
        self.uid = uid
        self.zone_id = zone_id
        self.env = env  # value of config.ENVS
        self.trace_id = trace_id
        self.extras = extras

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __str__(self):
        return "uid:{},zone_id:{},trace_id:{}".format(
            self.uid, self.zone_id, self.trace_id
        )

    def debug_str(self):
        return str(self.__dict__)


if __name__ == "__main__":
    ctx = Context(
        1,
        288300748311436289,
        1,
        {},
        {"username": "admin"},
        998300748311436289,
    )
    print(ctx)
    print(ctx.debug_str())
