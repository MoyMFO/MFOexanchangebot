from importlib.metadata import distribution
import pandas as pd
import numpy as np
from fitter import Fitter


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
        distribution = Fitter(self.prices_for_analysis)
        # Fit distribution
        distribution.fit()
        # Get parameters of the best distribution
        best_dist_params = distribution.get_best('sumsquare_error')
        return {'distribution_name': list(best_dist_params.keys())[0], 
                'mean': best_dist_params[list(best_dist_params.keys())[0]]['loc']}



class DesitionMaker:

    def __init__(self, next_expected_value: float) -> None:
        self.next_expected_value = next_expected_value
        
    def destion_maker(self):
        array_to_analize = np.array_split(self.prices_list,3)
        array_to_analize = [np.mean([array_to_analize[i]]) for i in range(len(array_to_analize))]

        if (array_to_analize[2] > array_to_analize[1]) and (array_to_analize[1] > array_to_analize[0]):
            self.prices_list.clear()
            return print("buy")
        elif (array_to_analize[2] < array_to_analize[1]) and (array_to_analize[1] < array_to_analize[0]):
            self.prices_list.clear()
            return print("sell")
        else:
            self.prices_list.clear()
            return print("hold")
