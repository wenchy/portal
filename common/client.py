# gRPC Python examples: https://github.com/grpc/grpc/tree/master/examples/python
import grpc

from core import context

# NOTE: In gPRC Python, the metadata key must be lower case，otherwise, you will
# encounter "TypeError: not all arguments converted during string formatting".
MDKeyPacketHeaderBin = "x-packet-header-bin"


def gen_metadata(uid, key=0):
    header = {} # TODO: protocol_pb2.PacketHeader()
    header.type = 1
    header.uid = uid
    header.upseq = 0  # TODO: sequence

    metadata = (
        (MDKeyPacketHeaderBin, header.SerializeToString()),
        ("test-accesstoken", "gRPC Python is great"),
    )
    return metadata


# def get_player(ctx):
#     addr = "localhost:9093"
#     req = test_service_pb2.GetPlayerRequest()
#     with grpc.insecure_channel(addr) as channel:
#         stub = test_service_pb2_grpc.InnerGameServiceStub(channel)
#         response, call = stub.GetPlayer.with_call(req, metadata=gen_metadata(ctx.uid))

#     return response

