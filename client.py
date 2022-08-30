import websockets
import json
from model import DecisionMaker, PriceForecast, DataTracker, SavingResults
import sys
from datetime import datetime


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
            actions_counter = 0
            while True:
                prices = json.loads(await ws.recv())
                try:
                    orderbooks.append(prices['payload'])
                    if len(orderbooks) == 200:
                        print('In condition')
                        sys.stdout.flush()
                        # Instance for mid_price or wighted_mid_price
                        model_data = DataTracker(orderbooks=orderbooks)
                        
                        # Measure selection
                        prices_for_analysis = model_data.mid_price()

                        # Price Forecast
                        forecast_results = PriceForecast(prices_for_analysis=prices_for_analysis)
                        forecast_results = forecast_results.next_expected_value()
                        print('After forecast results')
                        print(forecast_results['mean'])
                        print(forecast_results['distribution_name'])
                        sys.stdout.flush()
                        # Instance DesisionMaker
                        
                        trading_action = DecisionMaker(next_expected_value=forecast_results['mean'],
                                                       prices_for_analysis=prices_for_analysis,
                                                       book_name=self.book_name, actions_counter=actions_counter,
                                                       price_percentage=0.00009)
                        # Trading desicion
                        decision = trading_action.decision_maker()
                        print(decision)
                        sys.stdout.flush()
                        # Saving Results
                        saver = SavingResults()
                        saver = saver.save_transaction(id_transaction=str(datetime.now()), 
                                               expected_value=forecast_results['mean'],
                                               last_price=prices_for_analysis[-1],
                                               distribution=forecast_results['distribution_name'],
                                               mxn_balance=decision['mxn_balance'],
                                               action=decision['order_type'])
                        # Clear Orderbooks
                        
                        orderbooks.clear()
                        actions_counter += 1
                        print(actions_counter)
                        sys.stdout.flush()
                        #break
                        
                    #list_prices.append(prices['payload'][0]['r']) #prices['payload'][0]['r']
                    #DesitionMaker(list_prices).desition_model()
                    #print(f'this is l: {list_prices}')
                    #sys.stdout.flush()
                except:
                    pass
            #return forecast_results.next_expected_value()         

