class PacketHeader(object):
    def __init__(
        self,
        uid: int,
        method_id: int,
    ):
        self.uid = uid
        self.method_id = method_id

    def __getitem__(self, key):
        return self.__dict__.get(key)
    

def parse_method_id(method_descriptor):
    # TODO
    return 0