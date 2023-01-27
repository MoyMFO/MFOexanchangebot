import time
import hmac
import hashlib
import requests
import json
import pandas as pd
import numpy as np


class BitsoApiConn:

  def __init__(self, method_type, request_path, parameters = None) -> None:
    self.method_type = method_type
    self.request_path = request_path
    self.parameters = parameters

  def auth_header(self):
      bitso_key = ""      
      bitso_secret = ""
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

  def __init__(self, currency: str = None):
      self.currency = currency

  def available_money(self):
      bitsoconn = BitsoApiConn("GET", "/v3/balance/")
      response = requests.get("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
      balances = pd.DataFrame(json.loads(response.content)["payload"]["balances"])
      balance_mxn = float(balances[balances["currency"] == "mxn"]["available"].values[0])
      if balance_mxn >= 50:
        return balance_mxn
      else:
        return False

  def existing_order(self) -> bool:
    bitsoconn = BitsoApiConn("GET", "/v3/open_orders/")
    response = requests.get("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
    existing_order = json.loads(response.content)["payload"]
    if len(existing_order) == 0:
      return False
    else:
      return True

  def existing_crypto(self):
    bitsoconn = BitsoApiConn("GET", "/v3/balance/")
    response = requests.get("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
    balances = pd.DataFrame(json.loads(response.content)["payload"]["balances"])
    balance_specific_currency = float(balances[balances["currency"] == self.currency]["available"].values[0])
    if balance_specific_currency > 0.00020:
      return balance_specific_currency
    else:
      return False
  
  def last_trade_sell_price(self) -> float:
      parameters = {"book": self.currency, "limit": 30}
      bitsoconn = BitsoApiConn("GET", "/v3/user_trades/", parameters=parameters)
      response = requests.get("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      sell_trades = pd.DataFrame(json.loads(response.content)["payload"])[["side", "price", "created_at"]]
      sell_trades = float(sell_trades[sell_trades["side"] == "sell"]['price'].iloc[0])
      return sell_trades
  
  def last_trade_buy_price(self) -> float:
      parameters = {"book": self.currency, "limit": 30}
      bitsoconn = BitsoApiConn("GET", "/v3/user_trades/", parameters=parameters)
      response = requests.get("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      buy_trades = pd.DataFrame(json.loads(response.content)["payload"])[["side", "price", "created_at"]]
      buy_trades = float(buy_trades[buy_trades["side"] == "buy"]['price'].iloc[0])
      return buy_trades

class OrdersPlacement:
      
  def __init__(self, book, balance_mxn=None, balance_crypto_currency=None,
               last_price=None, price_percentage=None):
      self.book = book
      self.balance_mxn = balance_mxn
      self.balance_crypto_currency = balance_crypto_currency
      self.last_price = last_price
      self.price_percentage = price_percentage

  def __quantity_mxn_balance_to_trade(self) -> float:
    return np.round(((self.balance_mxn*.50)/self.last_price), 5)

  def __quantity_crypto_balance_to_trade(self) -> float:
    return np.round((self.balance_crypto_currency * .50), 5)

  @property
  def limit_price_buy(self) -> float:
    return np.round(self.last_price * (1 - self.price_percentage - 0.00001), 2)
  
  @property
  def limit_price_sell(self) -> float:
    return np.round(self.last_price * (1 + self.price_percentage), 2)

  def buy(self):
      parameters = {"book": self.book, "side":"buy", "type":"limit", "major": self.__quantity_mxn_balance_to_trade(), "price": self.limit_price_buy}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response = requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)
  
  def sell(self):
      parameters = {"book": self.book, "side":"sell", "type":"limit", "major": self.__quantity_crypto_balance_to_trade(), "price": self.limit_price_sell}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response =  requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)

  def cancel_order(self):
      bitsoconn = BitsoApiConn("DELETE", "/v3/orders/all")
      response =  requests.delete("https://api.bitso.com" + bitsoconn.request_path, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)
#wallet_information = WalletInformation(currency='btc') 
#existing_order = wallet_information.existing_order()
#mxn_balance = wallet_information.available_money()
#crypto_balance = wallet_information.existing_crypto()

#print(existing_order)
#print(mxn_balance)
#print(crypto_balance)

#order = OrdersPlacement(book='btc_mxn', balance_mxn=mxn_balance, balance_crypto_currency=crypto_balance, last_price=460266.25, price_percentage=0.97)
#order.buy()