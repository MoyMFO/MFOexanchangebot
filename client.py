import websockets
import json
from model import DesitionMaker
import sys

class PricesStreaming:

    def __init__(self, book_name: str):
        self.book_name = book_name

    async def prices_listener(self):
        uri = 'wss://ws.bitso.com/'
        async with websockets.connect(uri) as ws:
            conn_trades = json.dumps({ 'action': 'subscribe', 'book': self.book_name, 'type': 'orders' })
            await ws.send(conn_trades)
            print(f">>> {conn_trades}")
            sys.stdout.flush()
            list_prices = []
            i = 0
            while True and i < 10:
                prices = json.loads(await ws.recv())
                try:
                    list_prices.append(prices['payload']['bids'])
                    #print(f"<<< {prices['payload']['bids']}")
                    sys.stdout.flush()
                    #list_prices.append(prices['payload'][0]['r']) #prices['payload'][0]['r']
                    #DesitionMaker(list_prices).desition_model()
                    #print(f'this is l: {list_prices}')
                    #sys.stdout.flush()
                except:
                    pass
                i+=1
            return list_prices                    

