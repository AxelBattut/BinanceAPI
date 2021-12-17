# -*- coding: utf-8 -*-

import requests
import hashlib
import sqlite3
import hmac


api_key="yourapikey"
secret_key="yoursecretkey"
base_url ="https://api2.binance.com"


#GET PART
def getAvaibleCryptocurrencies():
    r = requests.get(base_url + "/api/v3/exchangeInfo")
    
    print(type(r.json()["symbols"]))
    listeTokenAvaible = []
    for symbol in r.json()["symbols"]:
        if symbol["baseAsset"] not in listeTokenAvaible:
            listeTokenAvaible.append(symbol["baseAsset"])
    return listeTokenAvaible

def getDepth(symbol,ask,bid): ## true false pour display l'ask et false true pour disp le bid 
    r=requests.get(base_url + "/api/v3/depth?symbol=" + symbol +"&limit=1")
    print(r.json())
    if(ask==False and bid==True):
        print("bid : " + str(r.json()['bids'][0][0]))
        return(r.json()['bids'][0][0])
    else:
        print("ask : " + str(r.json()['asks'][0][0]))
        return(r.json()['asks'][0][0])

def getOrderBookForAsset(symbol,limit):
    r=requests.get(base_url + "/api/v3/depth?symbol=" + symbol +"&limit=" + str(limit))
    return (r.json()['asks'],r.json()['bids'])




#SQLITE PART

def firstinsert(a,connection):
    cursor = connection.cursor() #on se connecte 
    
    """req = "create table candles(id integer primary key autoincrement,openTime int,open text, high text,low text, close text,volume text,closeTime int)"
    cursor.execute(req) """
    #on cree la db
    #CETTE ACTION EST A EFFECTUER UNIQUEMENT LA PREMIERE FOIS, si vous ne l'effectuez pas vous obtiendrez une erreur car aucune db ne sera créée
    
    requete = f"insert into candles (openTime ,open , high ,low , close ,volume ,closeTime) values ({a[0]},{a[1]},{a[2]},{a[3]},{a[4]},{a[5]},{a[6]})"
    cursor.execute(requete) #on l'implemente
    connection.commit()


def refreshDataCandle(symbol,Periode): #on fait appel à la fct insertcandles pour notre premiere creation de bdd
    r = requests.get(base_url+ "/api/v3/klines?symbol=" + symbol +"&interval=" +Periode)
    connection = sqlite3.connect('MYBDD.db')
    for a in r.json():
        firstinsert(a,connection)  
    connection.close()

def candlModify(a,connection):
    cursor = connection.cursor()
    requete = f"insert into trades (idTrade ,price , qty ,quoteqty , time ,isBuyerMaker ,isbestMatch ) values ({a['id']},{a['price']},{a['qty']},{a['quoteQty']},{a['time']},{a['isBuyerMaker']},{a['isBestMatch']})"
    cursor.execute(requete)
    connection.commit()

def refreshData(symbol):
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r = requests.get(base_url + "/api/v3/historicalTrades?symbol=" + symbol,headers=headers)
    connection = sqlite3.connect('ApiBinance.db')
    for a in r.json():
        candlModify(a,connection)
    connection.close()

#POST PART 

def makeOrder(symbol,side,type,timeInForce,quantity,price,):
    secret = secret_key
    timestamp = requests.get(base_url + "/api/v3/time").json()["serverTime"]
    query_string = "symbol="+symbol+"&side="+side+"&type="+type +"&timeInForce="+timeInForce+"&quantity="+quantity+ "&price="+price+ "&timestamp="+str(timestamp)
    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r = requests.post(base_url + "/api/v3/order?"
                      + "symbol="+symbol
                      + "&side="+side
                      + "&type="+type
                      + "&timeInForce="+timeInForce
                      + "&quantity="+quantity
                      + "&price="+price
                      + "&timestamp="+str(timestamp)
                      + "&signature="+signature,headers=headers)
    print(r.json())
    return r.json()

def cancelOrder(symbol,orderId):
    secret = secret_key
    timestamp = requests.get(base_url + "/api/v3/time").json()["serverTime"]
    query_string = "symbol="+symbol+"&orderId="+orderId+"&timestamp="+str(timestamp)
    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r=requests.delete(base_url+"/api/v3/order?symbol="+symbol+"&orderId="+orderId+"&timestamp="+str(timestamp)+"&signature="+signature,headers=headers)
    print(r.text)



if __name__ == '__main__':
    print(getAvaibleCryptocurrencies())
    ##print(getDepth('BTCUSDT',False,True))
    ##print(getOrderBookForAsset('DOGEUSDT', 100))
   
    
    ##refreshDataCandle('BTCUSDT', '5m') #FIRST GO TO LINE 47 AND CREATE DATABASE ONCE FOREVER (or download my given db)
    ##refreshData('BTCUSDT')
    
    
    ##OrderId = makeOrder('BTCUSDT','SELL','LIMIT','GTC','0.1','40000')['OrderId']
    ##cancelOrder('BTCUSDT',str(OrderId))
   
    