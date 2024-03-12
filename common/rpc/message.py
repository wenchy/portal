import struct
import copy
import itertools


class Error(Exception):
    pass


class UnpackError(Error):
    pass


class NeedData(UnpackError):
    pass


class PackError(Error):
    pass


class _MetaPacket(type):
    def __new__(cls, clsname, clsbases, clsdict):
        t = type.__new__(cls, clsname, clsbases, clsdict)
        st = getattr(t, '__hdr__', None)
        if st is not None:
            clsdict['__slots__'] = [x[0] for x in st] + ['data']
            t = type.__new__(cls, clsname, clsbases, clsdict)
            t.__hdr_fields__ = [x[0] for x in st]
            t.__hdr_fmt__ = getattr(t, '__byte_order__', '>') + \
                ''.join([x[1] for x in st])
            t.__hdr_len__ = struct.calcsize(t.__hdr_fmt__)
            t.__hdr_defaults__ = dict(zip(
                t.__hdr_fields__, [x[2] for x in st]))
        return t


class Packet(object):

    __metaclass__ = _MetaPacket

    def __init__(self, *args, **kwargs):
        self.data = ''
        if args:
            try:
                self.unpack(args[0])
            except struct.error:
                if len(args[0]) < self.__hdr_len__:
                    raise NeedData
                raise UnpackError('invalid %s: %r' %
                                  (self.__class__.__name__, args[0]))
        else:
            for k in self.__hdr_fields__:
                setattr(self, k, copy.copy(self.__hdr_defaults__[k]))
            for k, v in kwargs.iteritems():
                setattr(self, k, v)

    def __len__(self):
        return self.__hdr_len__ + len(self.data)

    def __getitem__(self, k):
        try:
            return getattr(self, k)
        except AttributeError:
            raise KeyError

    def __repr__(self):
        l = ['%s=%r' % (k, getattr(self, k))
             for k in self.__hdr_defaults__
             if getattr(self, k) != self.__hdr_defaults__[k]]
        if self.data:
            l.append('data=%r' % self.data)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(l))

    def __str__(self):
        return self.pack_hdr() + str(self.data)

    def pack_hdr(self):
        try:
            return struct.pack(self.__hdr_fmt__,
                               *[getattr(self, k) for k in self.__hdr_fields__])
        except struct.error:
            vals = []
            for k in self.__hdr_fields__:
                v = getattr(self, k)
                if isinstance(v, tuple):
                    vals.extend(v)
                else:
                    vals.append(v)
            try:
                return struct.pack(self.__hdr_fmt__, *vals)
            except struct.error, e:
                raise PackError(str(e))

    def pack(self):
        return str(self)

    def unpack(self, buf):
        for k, v in itertools.izip(self.__hdr_fields__,
                                   struct.unpack(self.__hdr_fmt__, buf[:self.__hdr_len__])):
            setattr(self, k, v)
        self.data = buf[self.__hdr_len__:]


class AppHeader(Packet):
    __hdr__ = (
        ('header_size', 'I', 0),  # uint32
        ('body_size', 'I', 0),  # uint32
        ('resv', 'I', 0),  # uint32
    )
    __byte_order__ = '!'


class ProtobufRequest(AppHeader):
    def __init__(self, header, body):
        AppHeader.__init__(self)
        header_data = header.SerializeToString()
        body_data = body.SerializeToString()
        self.data = header_data + body_data
        self.header_size = len(header_data)
        self.body_size = len(body_data)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return AppHeader.__str__(self)


class ProtobufResponse(AppHeader):
    def __init__(self, header_type, body_type):
        AppHeader.__init__(self)
        self.header = header_type()
        self.body = body_type()

    def unpack(self, buf):
        if len(buf) < AppHeader.__len__(self):
            raise NeedData("Timeout: buf len %d < hdr len %d"
                           % (len(buf), AppHeader.__len__(self)))
        AppHeader.unpack(self, buf)
        if self.header_size + self.body_size > len(self.data):
            raise NeedData("data len %d < len in hdr %d"
                           % (len(self.data), self.header_size + self.body_size))
        header_data = self.data[:self.header_size]
        self.header.ParseFromString(header_data)
        body_data = self.data[self.header_size:]
        self.body.ParseFromString(body_data)