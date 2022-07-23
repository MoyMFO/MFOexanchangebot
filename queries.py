from inspect import Parameter
import time
import hmac
import hashlib
from urllib import response
import requests
import json
import pandas as pd
from sympy import Order


class BitsoApiConn:

  def __init__(self, method_type, request_path, parameters = None):
    self.method_type = method_type
    self.request_path = request_path
    self.parameters = parameters

  def auth_header(self):
      
      nonce =  str(int(round(time.time() * 1000)))
      message = nonce+self.method_type+self.request_path
      if self.method_type == "POST":
            message += json.dumps(self.parameters)
      #Create signature      
      signature = hmac.new(bitso_secret.encode('utf-8'),
                                                message.encode('utf-8'),
                                                hashlib.sha256).hexdigest()
      #Build header
      auth_header = 'Bitso %s:%s:%s' % (bitso_key, nonce, signature)
      return auth_header
    

class WalletInformation:

  def __init__(self, currency = None):
      self.currency = currency

  def available_money(self):
      bitsoconn = BitsoApiConn("GET", "/v3/balance/")
      response = requests.get("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
      balances = pd.DataFrame(json.loads(response.content)["payload"]["balances"])
      balance_mxn = float(balances[balances["currency"] == "mxn"]["available"].values[0])
      if balance_mxn >= 50:
        return balance_mxn
      else:
        return print(False)

  def existing_long_position(self):
    bitsoconn = BitsoApiConn("GET", "/v3/balance/")
    response = requests.get("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
    balances = pd.DataFrame(json.loads(response.content)["payload"]["balances"])
    balance_specific_currency = float(balances[balances["currency"] == self.currency]["available"].values[0])
    if balance_specific_currency > 0:
      return balance_specific_currency
    else:
      return print(False)

class OrdersPlacement:
      
  def __init__(self, book, balance_mxn=None, balance_crypto_currency=None):
      self.book = book
      self.balance_mxn = balance_mxn
      self.balance_crypto_currency = balance_crypto_currency

  def buy(self):
      parameters = {"book": self.book, "side":"buy", "type":"market", "minor": self.balance_mxn}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response = requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)
  
  def sell(self):
      parameters = {"book": self.book, "side":"sell", "type":"market", "major": self.balance_crypto_currency}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response =  requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)

  def cancel(self):
      pass


test_wallet_information = WalletInformation(currency="bat")
#test_buy = OrdersPlacement(book="btc_mxn", balance_mxn = test_wallet_information.available_money())
#test_buy.buy()

#test_sell = OrdersPlacement(book="bat_mxn", balance_crypto_currency=test_wallet_information.existing_long_position())
#test_sell.sell()
