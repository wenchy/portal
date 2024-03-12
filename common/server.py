import sys

sys.path.append("protocol")

from concurrent import futures
import logging

import grpc


# class InnerMailServicer(test_service_pb2_grpc.InnerMailServicer):

#     def Send(self, request, context):
#         for key, value in context.invocation_metadata():
#             print("Received initial metadata: key=%s value=%s" % (key, value))
#         print("request: " + str(request))
#         context.set_trailing_metadata(
#             (
#                 ("checksum-bin", b"I agree"),
#                 ("retry", "false"),
#             )
#         )
#         return test_pb2.SCInnerMailSend()


# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     test_service_pb2_grpc.add_InnerMailServicer_to_server(
#         InnerMailServicer(), server
#     )
#     server.add_insecure_port("[::]:9093")
#     server.start()
#     server.wait_for_termination()


# if __name__ == "__main__":
#     logging.basicConfig()
#     serve()
