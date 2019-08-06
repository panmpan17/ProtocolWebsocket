# Protocol Websocket
Websocket 用於網站的 socket 協議，此套件用於幫助伺服器與客戶端溝通，訊息內容由 Json 包裝方便讀寫。

Websocket is a socket protocol for web browswer. <br>
This library help server and client communicate by only using json to transfer data.

## Example
```python
from protocolws import WebsocketServer


class Server(WebsocketServer):
    def disconnect(self, _id, ws):
        # _id is client special id, use for identify user
        # ws is websocket client class
        pass
    
    # inspire by http the request have method and data
    def ECHO(self, _id, ws, data):
        yield from self.send(ws, {"method": "ECHO", "data": data})


server = Server()
server.set_up("127.0.0.1", 8080)
server.run_forever()

```