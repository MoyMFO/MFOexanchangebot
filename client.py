import websockets
import json
from model import DesitionMaker, PriceForecast, DataTracker
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
            orderbooks = []
            while True:
                prices = json.loads(await ws.recv())
                try:
                    orderbooks.append(prices['payload'])
                    if len(orderbooks) == 200:
                        # Instance for mid_price or wighted_mid_price
                        model_data = DataTracker(orderbooks=orderbooks)
                        
                        # Measure selection
                        prices_for_analysis = model_data.wighted_mid_price()

                        # Price Forecast
                        results = PriceForecast(prices_for_analysis=prices_for_analysis)

                        # Decision making
                        # Make a first trade
                        # Instance DesisionMaker

                        break
                    #list_prices.append(prices['payload'][0]['r']) #prices['payload'][0]['r']
                    #DesitionMaker(list_prices).desition_model()
                    #print(f'this is l: {list_prices}')
                    #sys.stdout.flush()
                except:
                    pass
            return results.next_expected_value()         

