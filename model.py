import pandas as pd
import numpy as np
from fitter import Fitter
import sqlite3
from queries import WalletInformation, OrdersPlacement

class DataTracker:
    
    def __init__(self, orderbooks: list) -> None:
        self.orderbooks = orderbooks

    def mid_price(self) -> np.array:
        bids = np.array([ob['bids'][0]['r'] for ob in self.orderbooks])
        asks = np.array([ob['asks'][0]['r'] for ob in self.orderbooks])
        mid_price = (bids + asks)/2
        return mid_price
        
    def wighted_mid_price(self) -> np.array:
        bids_price = np.array([ob['bids'][0]['r'] for ob in self.orderbooks])
        asks_price = np.array([ob['asks'][0]['r'] for ob in self.orderbooks])
        bids_volume = np.array([ob['bids'][0]['v'] for ob in self.orderbooks])
        asks_volume = np.array([ob['asks'][0]['v'] for ob in self.orderbooks])
        weighted_mid_price = (asks_price * (bids_volume / (bids_volume + asks_volume))
                             + bids_price * (asks_volume / (bids_volume + asks_volume)))
        return weighted_mid_price


class PriceForecast:

    def __init__(self, prices_for_analysis: np.array) -> None:
        self.prices_for_analysis = prices_for_analysis
    
    def next_expected_value(self) -> dict:
        # Instance Distribution of 200 weigthed mid prices 
        distribution = Fitter(self.prices_for_analysis, distributions=['johnsonsu', 'beta', 'pearson3'])
        # Fit distribution
        distribution.fit()
        # Get parameters of the best distribution
        best_dist_params = distribution.get_best('sumsquare_error')
        return {'distribution_name': list(best_dist_params.keys())[0], 
                'mean': best_dist_params[list(best_dist_params.keys())[0]]['loc']}



class DecisionMaker:

    def __init__(self, next_expected_value: float,
                 prices_for_analysis: np.array,
                 book_name: str, actions_counter: int,
                 price_percentage: float) -> None:
        self.next_expected_value = next_expected_value
        self.prices_for_analysis = prices_for_analysis
        self.book_name = book_name
        self.actions_counter = actions_counter
        self.price_percentage = price_percentage

    def decision_maker(self) -> dict:
        
        # Expected Value
        next_expected_value = np.round(self.next_expected_value, 2)
        last_price = np.round(self.prices_for_analysis[-1], 2)

        # Database Comprobation
        if self.actions_counter == 0:
            last_decision = 'Hold'
        else:
            last_decision = SavingResults().last_decision()

        # Wallet Information
        wallet_information = WalletInformation(currency=self.book_name[0:3]) 
        existing_order = wallet_information.existing_order()
        mxn_balance = wallet_information.available_money()
        crypto_balance = wallet_information.existing_crypto()
        print(f'this is the last price {last_price}')
        # Order placement Instance
        order = OrdersPlacement(book=self.book_name, balance_mxn=mxn_balance,
                                 balance_crypto_currency=crypto_balance, last_price=last_price,
                                 price_percentage=self.price_percentage)

        if ((next_expected_value > last_price) and (mxn_balance != False) 
            and (last_price < wallet_information.last_trade_sell_price())):
            order.cancel_order()
            order.buy()
            return {'order_type': 'Buy', 'mxn_balance': mxn_balance} 
        elif next_expected_value == last_price:
            return {'order_type': 'Hold', 'mxn_balance': mxn_balance}
        elif ((next_expected_value < last_price) and  (crypto_balance != False)
             and (last_price > wallet_information.last_trade_buy_price())):
            order.cancel_order()
            order.sell()
            return {'order_type': 'Sell', 'mxn_balance': mxn_balance}
        else:
            return {'order_type': 'Hold', 'mxn_balance': mxn_balance}

class SavingResults:

    def __init__(self) -> None:
        pass

    @staticmethod
    def save_transaction(id_transaction: str, expected_value: float,
                         last_price: float, distribution: str, mxn_balance:float,
                         action: str) -> None:
        conn = sqlite3.connect('transactions.db')
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS model_performance 
        (
        id_transaction TEXT PRIMARY KEY, 
        expected_value REAL,
        last_price REAL,
        distribution TEXT,
        mxn_balance REAL,
        action TEXT
        )
        """)

        cur.execute("INSERT INTO model_performance VALUES (?, ?, ?, ?, ?, ?)",
        (id_transaction, expected_value, last_price, distribution, mxn_balance, action))
        conn.commit()
        conn.close()
        return None
    
    @staticmethod
    def last_decision() -> str:
        conn = sqlite3.connect('transactions.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM model_performance")
        transactions = cur.fetchall()
        last_decision = transactions[-1][-1]
        conn.close()

        return last_decision