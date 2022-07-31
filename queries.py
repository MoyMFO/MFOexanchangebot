import time
import hmac
import hashlib
import requests
import json
import pandas as pd
from sklearn.linear_model import lasso_path
import numpy as np


class BitsoApiConn:

  def __init__(self, method_type, request_path, parameters = None):
    self.method_type = method_type
    self.request_path = request_path
    self.parameters = parameters

  def auth_header(self):
      bitso_key = "IBQdAgHOqa"      
      bitso_secret = "4b3bd96deaac38652da20e0505a44ffb"
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

  def existing_order(self):
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
    if balance_specific_currency > 0:
      return balance_specific_currency
    else:
      return False

class OrdersPlacement:
      
  def __init__(self, book, balance_mxn=None, balance_crypto_currency=None, last_price=None):
      self.book = book
      self.balance_mxn = balance_mxn
      self.balance_crypto_currency = balance_crypto_currency
      self.last_price = last_price

  def buy(self):
      parameters = {"book": self.book, "side":"buy", "type":"limit", "major": 0.00005154, "price": self.last_price}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response = requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)
  
  def sell(self):
      parameters = {"book": self.book, "side":"sell", "type":"limit", "major": self.balance_crypto_currency, "price": self.last_price}
      bitsoconn = BitsoApiConn("POST", "/v3/orders/", parameters=parameters)
      response =  requests.post("https://api.bitso.com" + bitsoconn.request_path, json = parameters, headers={"Authorization": bitsoconn.auth_header()})
      return print(response.content)

