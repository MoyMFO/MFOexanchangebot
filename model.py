from numpy import array
import pandas as pd
import numpy as np

class DesitionMaker:

    def __init__(self, prices_list):
        self.prices_list = prices_list

    def desition_model(self):
        if len(self.prices_list) == 12:
            return self.destion_maker()
        

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
