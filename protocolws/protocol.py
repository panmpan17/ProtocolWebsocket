from datetime import datetime
import logging

import asyncio
import asyncws
import json
import random
import string


class ErrMsg:
    DATA_PARSE_WRONG = {
        "method": "ERROR",
        "reason": "Data Parse Error"}

    MISSING_ARGUMENT = {
        "method": "ERROR",
        "reason": "Missing Argument"}

    WRONG_METHOD = {
        "method": "ERROR",
        "reason": "Method not exist"}


class Method:
    def __init__(self, method_json):
        for method in method_json:
            self.__setattr__(method, method)


class WebsocketServer:
    def __init__(self, log=True, log_option={}):
        """
        :params log(Boolean): Server log when data recieve or send.
        :params log_option(Dict): Logs option, See more in documentation.
        """

        self.server = None
        self.lock = asyncio.Lock()

        self.connected = {}

        self.log = log
        self.log_date = True
        self.log_time = True
        self.log_client_id = True
        self.log_data = True

    def _checkdata(self, data, keys):
        for key in keys:
            if key not in data:
                return False
        return True

    def request_log(self, _id, method, data):
        now = datetime.now()
        log = "\033[0;33m"

        if self.log_date:
            log += now.strftime("%D")
            if self.log_time:
                log += now.strftime(" %T")
        elif self.log_time:
            log += now.strftime("%T")

        log += "\x1b[0m"

        if self.log_client_id:
            log += f" \033[0;36m{_id}\x1b[0m"

        log += f" \033[0;34m{method}\x1b[0m "

        if self.log_data:
            log += str(data)

        print(log)

    def run(self, ip, port):
        self.server = asyncws.start_server(self.handle_client, ip, port)
        asyncio.get_event_loop().run_until_complete(self.server)

        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            pass

    def welcome(self, _id, ws):
        with (yield from self.lock):
            self.connected[_id] = {"id": _id, "ws": ws}
            print(f"\033[0;32mConnect: {_id}\x1b[0m")

    def disconnect(self, _id, ws):
        with (yield from self.lock):
            self.connected.pop(_id)
            print(f"\033[0;31mDisconnect: {_id}\x1b[0m")

    def send(self, ws, data):
        yield from ws.send(json.dumps(data))

    @asyncio.coroutine
    def handle_client(self, ws):
        _id = "".join(random.sample(string.ascii_letters, 16))
        yield from self.welcome(_id, ws)

        while True:
            try:
                data = yield from ws.recv()

                # player disconnect
                if data is None:
                    yield from self.disconnect(_id, ws)
                    return

                data = json.loads(data)

                self.request_log(_id, "SEND", data)
            except json.decoder.JSONDecodeError:
                self.request_log(_id, "ERROR", data)
                yield from self.send(ws, ErrMsg.DATA_PARSE_WRONG)

            if "method" not in data:
                yield from self.send(ws, ErrMsg.MISSING_ARGUMENT)
                continue

            try:
                method_handler = self.__getattr__(data["method"])
            except AttributeError:
                print(f"\033[0;31mMethod '{data['method']}' not exist\x1b[0m")
                yield from self.send(ws, ErrMsg.WRONG_METHOD)
                continue

            try:
                method_handler(_id, ws, data)
            except Exception as e:
                print(f"\033[0;31mExcpetion occur when handling data")
                logging.exception(e)
                print("\x1b[0m")


if __name__ == "__main__":
    server = WebsocketServer()
    server.run("localhost", 12345)