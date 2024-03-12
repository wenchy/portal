import http.client as httpclient
import urllib3
from message import *
from util import *
from core.logger import log
from google.protobuf import service
from google.protobuf import text_format


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HTTPConnectionPoolManager(object):
    """
    Note:
    A singleton for managing HTTP connection pool.
    Keep-alive and HTTP connection pooling are 100% automatic, thanks to urllib3.
    """

    __metaclass__ = Singleton

    def __init__(
        self, num_pools=10, maxsize=200, timeout=urllib3.Timeout(connect=2.0, read=2.0)
    ):
        # block=True:
        # This is a useful side effect for particular multithreaded situations where one does not want to use more
        # than maxsize connections per host to prevent flooding
        self.manager = urllib3.PoolManager(
            num_pools=num_pools, maxsize=maxsize, block=True
        )

    def connection_from_host(self, host, port=None, scheme="http", pool_kwargs=None):
        return self.manager.connection_from_host(host, port, scheme, pool_kwargs)

    @property
    def num_pools(self):
        return len(self.manager.pools)


# Python Generated Code: https://developers.google.com/protocol-buffers/docs/reference/python-generated#service
# RpcController: https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.RpcController


class RpcController(service.RpcController):

    def __init__(self, entity_id, uid=0, dst="", router_type=0, router_key=0):
        self.Reset()
        self.error = 0
        self.entity_id = entity_id
        self.uid = uid
        self.dst = dst
        self.router_type = router_type
        self.router_key = router_key

    def Reset(self):
        self.entity_id = 0
        self.error = 0
        self.uid = 0
        self.dst = ""
        self.router_type = 0
        self.router_key = 0

    def Failed(self):
        return self.error != 0


# RpcChannel: https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.RpcChannel


class RpcChannel(service.RpcChannel):

    def __init__(self, ctx, protocol="http"):
        self.ctx = ctx
        self.protocol = protocol

    def CallMethod(
        self, method_descriptor, rpc_controller, request, response_class, done
    ):
        header = PacketHeader()
        header.uid = rpc_controller.uid
        header.method_id = parse_method_id(method_descriptor)
        log.debug("request packet header: %s", str(header))

        _request = ProtobufRequest(header, request)
        _rsp_data = ""
        log.debugCtx(self.ctx, "start rpc request to gatesvr")
        ip = self.ctx.env["gate"]["ip"]
        port = self.ctx.env["gate"]["port"]
        if self.protocol == "http":
            client = httpclient.HTTPConnection(ip, port, timeout=5)
            body = str(_request)
            headers = {
                "Content-Type": "application/octet-stream",
            }
            client.request("POST", "/index/rpc", body, headers)
            res = client.getresponse()
            _rsp_data = res.read()
            if res.status != 200:
                rpc_controller.error = -1
                return "http failed\nstatus-line: %s %d %s\n%s" % (
                    res.version,
                    res.status,
                    res.reason,
                    _rsp_data,
                )

        elif self.protocol == "http-connection-pool":
            manager = HTTPConnectionPoolManager(num_pools=100, maxsize=100)
            pool = manager.connection_from_host(ip, port)
            body = str(_request)
            headers = {
                "Content-Type": "application/octet-stream",
            }
            res = pool.urlopen("POST", "/index/rpc", body=body, headers=headers)
            _rsp_data = res.data
            if res.status != 200:
                rpc_controller.error = -1
                return "http failed\nstatus-line: %s %d %s\n%s" % (
                    res.version,
                    res.status,
                    res.reason,
                    _rsp_data,
                )

            log.debug(
                "HTTPConnectionPoolManager|num_pools: %d, num_connections: %d, num_requests: %d",
                manager.num_pools,
                pool.num_connections,
                pool.num_requests,
            )

        _response = ProtobufResponse(PacketHeader, response_class)
        _response.unpack(_rsp_data)
        log.debug(
            "response packet header: %s",
            text_format.MessageToString(_response.header, as_utf8=True),
        )
        log.debug(
            "response packet body: %s",
            text_format.MessageToString(_response.body, as_utf8=True),
        )
        rpc_controller.error = _response.header.code
        rpc_controller.header = _response.header

        return _response.body
