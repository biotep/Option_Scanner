
import sys
import math
import time
from ib_insync import *
import datetime
import numpy as np
import pandas as pd

#symbol_to_download = sys.argv[1]
# BOUGHT 1 SPX CBOE Apr16'20 3280 PUT (SPX) @ 44.2 (UXXX0783)


def download_from_ib():
    ib = IB()
    try:
        if not ib.isConnected():
            print('not connected...trying to connect')
            ib.connect('3.212.53.57', 4002, clientId=13, timeout=10)
            #ib.connect('localhost', 7497, clientId=14)

    except:
        return 1001




    option_expiry = '20200417'
    SPY_put_atm = Option('SPX', option_expiry, 2440, 'P', 'SMART')
    ticker = ib.reqTickers(SPY_put_atm)

    # underlying contract
    c = Stock(symbol='BYND', exchange='SMART',
              primaryExchange='NASDAQ', currency='USD', localSymbol='BYND',
              tradingClass='NMS')

    c = Stock(conId=364036112, symbol='BYND', exchange='SMART',
              primaryExchange='NASDAQ', currency='USD', localSymbol='BYND',
              tradingClass='NMS')
    # get info for optionchain
    contract_info = {'underlyingSymbol': c.symbol,
                     'futFopExchange': '',
                     'underlyingSecType': c.secType,
                     'underlyingConId': c.conId}



    try:
        optionChains = ib.reqSecDefOptParams(**contract_info)
        # print relevant optionchain and check strikes
        oc = [el for el in optionChains if (option_expiry in el.expirations) & (el.exchange == 'SMART')]
    except:
        return 1002

    if ib.isConnected():
        ib.disconnect()

    time.sleep(1)
    #print(df0)
    print(oc)

download_from_ib()


