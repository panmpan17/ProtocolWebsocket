# Add top-level path to import library
import threading
import unittest
import asyncio
import asyncws
import time
import json
import ssl

import sys
sys.path.append("..")
from protocolws import WebsocketServer, ErrMsg

SOCKET_PORT = 12345

server = None
serverthread = None
wsocket = None

class Server(WebsocketServer):
    def ECHO(self, _id, ws, data):
        yield from self.send(ws, data)

    def NOTHING(self, _id, ws, data):
        print("Doing Nothing. YEAH.")

    def CLOSE(self, _id, ws, data):
        print("Closing Connection")
        return True


def setUpModule():
    global server, serverthread, wsocket

    server = Server()

    def begin():
        global wsocket
        server.set_up("localhost", SOCKET_PORT, loop=asyncio.new_event_loop(),
            ssl=ssl)
        wsocket = server.wsocket
        server.run_forever()

    serverthread = threading.Thread(target=begin)
    serverthread.start()
    print("Complete setup")


class WebsocketServerTestCase(unittest.TestCase):
    def setUp(self):
        self.url = "ws://localhost:" + str(SOCKET_PORT)

    def test_server(self):
        global server, serverthread, wsocket

        loop = asyncio.get_event_loop()
        websocket = loop.run_until_complete(asyncws.connect(self.url))
        loop.run_until_complete(self.non_ssl_server(websocket))

        # Send stop signal to server
        wsocket.send(b"stop")
        serverthread.join()

        serverthread = None
        server = None

    @asyncio.coroutine
    def non_ssl_server(self, websocket):
        yield from websocket.send('hello')
        data = yield from websocket.recv()
        data = json.loads(data)

        self.assertEqual(data["method"], ErrMsg.DATA_PARSE_WRONG["method"])
        self.assertEqual(data["reason"], ErrMsg.DATA_PARSE_WRONG["reason"])
        del data

        yield from websocket.send(json.dumps({"data": "nothing"}))
        data = yield from websocket.recv()
        data = json.loads(data)

        self.assertEqual(data["method"], ErrMsg.MISSING_ARGUMENT["method"])
        self.assertEqual(data["reason"], ErrMsg.MISSING_ARGUMENT["reason"])
        del data

        yield from websocket.send(json.dumps({"method": "WRONGMETHOD"}))
        data = yield from websocket.recv()
        data = json.loads(data)

        self.assertEqual(data["method"], ErrMsg.WRONG_METHOD["method"])
        self.assertEqual(data["reason"], ErrMsg.WRONG_METHOD["reason"])
        del data

        msg = {"method": "ECHO", "data": "ECHO... Echo... echo..."}
        yield from websocket.send(json.dumps(msg))
        data = yield from websocket.recv()
        data = json.loads(data)

        self.assertEqual(data["method"], msg["method"])
        self.assertEqual(data["data"], msg["data"])
        del data

        yield from websocket.send(json.dumps({"method": "NOTHING"}))

        msg = {"method": "CLOSE"}
        yield from websocket.send(json.dumps(msg))

    @asyncio.coroutine
    def ssl_server(self, websocket):
        pass
