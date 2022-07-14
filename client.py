import asyncio
import websockets
import json
from model import DesitionMaker


class PricesStreaming:

    def __init__(self, book_name: str):
        self.book_name = book_name

    async def prices_listener(self):
        uri = "wss://ws.bitso.com/"
        async with websockets.connect(uri) as ws:
            conn_trades = json.dumps({ "action": 'subscribe', "book": self.book_name, "type": 'trades' })
            await ws.send(conn_trades)
            print(f">>> {conn_trades}")
            
            list_prices = []
            while True:
                prices = json.loads(await ws.recv())
                try:
                    print(f"<<< {prices['payload'][0]}")
                    list_prices.append(prices['payload'][0]["r"])
                    DesitionMaker(list_prices).desition_model()
                    print(f"this is l: {list_prices}")
                except:
                    pass
                    

