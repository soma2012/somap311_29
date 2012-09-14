# coding:utf8

from twisted.web import server
from twisted.internet import reactor
from time import time


from jsonrpc.server import ServerEvents, JSON_RPC
from jsonrpc.proxy import JSONRPCProxy
import socket


class Client(JSONRPCProxy):

    def is_alive(self):
        """ josnrpc server 의 is_jsonrpc_alive함수를 콜해봐서 jsonrpc서버가 살아있는지 여부 판단한다.
        """
        try:
            self.call("is_jsonrpc_alive")
            return True
        except:
            return False

class Server:

    """ @summary: json rpc 서버
    """
    def __init__(self, event, port):
        self.port = int(port)
        root = JSON_RPC().customize(event)
        site = server.Site(root)
        reactor.listenTCP(self.port, site)
        self.name = self._name(event)

    def _name(self, event):
        name = str(event).replace("<class '__main__.", "").replace("'>", "")
        return name

    def run(self):
        print "[+] Start " + self.name + " ", self.port
        reactor.run()

    _RPC = ""

    def set_rpc(rpc_dict):

        global _RPC
        rpc = rpc_dict["default"]
        host = socket.gethostname()
        if host in rpc_dict:
            rpc = rpc_dict[host]
        _RPC = Client(rpc)

    def func(method, req, rpc="", more={}):

        if more:
            req.update(more)
        if rpc:
            return getattr(rpc, method)(**req)
        else:
            return getattr(_RPC, method)(**req)

    def get(loc_dict, more={}):

        """ locals()에서 self제거 하고 more가 있으면 합쳐서 리턴하는 함수. rpc 함수에서 주로 사용.
        """
        if "self" in loc_dict:
            loc_dict.pop("self")
        loc_dict.update(more)
        return loc_dict

