from ib_insync import *
import pandas as pd
import math
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

ib = IB()
ib.connect('3.212.53.57', 4002, clientId=13, timeout=10)

option_expiry = '20200417'

cds = ib.reqContractDetails(Option('EPD', option_expiry, exchange='SMART'))
options = [cd.contract for cd in cds]
tickers = [t for i in range(0, len(options), 100) for t in ib.reqTickers(*options[i:i + 100])]
ib.disconnect()
#=====================
spx = Stock('EPD', 'NYSE')
ib.qualifyContracts(spx)
[ticker] = ib.reqTickers(spx)
spx_value=ticker.marketPrice()

chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
chain = next(c for c in chains if c.tradingClass == 'EPD' and c.exchange == 'SMART')


strikes = [strike for strike in chain.strikes]

expirations = sorted(exp for exp in chain.expirations)
rights = ['P', 'C']

contracts = [Option('EPD', expiration, strike, right, 'SMART', tradingClass='EPD')
        for right in rights
        for expiration in expirations
        for strike in strikes]

tickers = ib.reqTickers(*contracts)



df = pd.DataFrame(columns=strikes, index=expirations)
for t in tickers:
    if not math.isnan(t.bid) and t.contract.right=='C':
        df[t.contract.strike, t.contract.lastTradeDateOrContractMonth]=t.bid

