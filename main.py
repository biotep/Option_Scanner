from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import  Select, TextInput, Button, Div, RadioButtonGroup, Paragraph, Tabs, TableColumn, DataTable, DateFormatter, PreText
import bokeh.palettes as bk_pal
import configparser
import time
from ib_insync import *
import asyncio
import numpy as np
import pandas as pd
import os
import os.path
from bs4 import BeautifulSoup
import getpass


from pathlib import Path
home = str(Path.home())

username = getpass.getuser()
config = configparser.ConfigParser()
configFile = home + '/Documents/Python/Ibis/config.ini'

config.read(configFile)
history_dir = config['History directory']['history_dir']
history_root = config['History directory']['history_dir']
server = config['Server']['server_document']
catalog_file = history_root+"catalog.csv"
ib_server = config['IB']['IB_Server']
ib_port = config['IB']['IB_Port']


class Gemini:
    def __init__(self):
        self.strikes = list(np.arange(1.0, 40.0, 0.5))
        self.expirations = ['20200403',
 '20200409',
 '20200417',
 '20200424',
 '20200501',
 '20200508',
 '20200515',
 '20200619',
 '20200918',
 '20210115',
 '20220121']
        self.view_setup()
        self.exchange = 'NYSE'

    def view_setup(self):


        self.text5 = Div(text="Ticker downloader:", width = 150)

        self.tickerdownloader = TextInput(value='', width = 80)
        self.tickerdownloadbutton = Button(label='Press to download', button_type='default', disabled=False, width = 50)
        self.tickerdownloadbutton.on_click(self.tickerdownloadbutton_handler)

        self.exchangebutton = RadioButtonGroup(labels=["NYSE", "NASDAQ"], active=0, width=140)
        self.exchangebutton.on_change("active", self.exchange)

        self.widgets = column(column(self.text5, self.tickerdownloader, self.tickerdownloadbutton, self.exchangebutton))
        main_row = row(self.widgets)
        layout = column(main_row)


        curdoc().add_root(layout)
        curdoc().title = "Stocks"



    def tickerdownloadbutton_handler(self):
        print('downloading ticker: ' + self.tickerdownloader.value)
        self.tickerdownloadbutton.label = 'downloading...'
        s = self.download_from_ibs(self.tickerdownloader.value)
        print("Control is back here :) ")
        if s.empty:
            print("returned an empty dataframe...")
            self.tickerdownloadbutton.button_type = 'danger'
            self.tickerdownloadbutton.label = 'download failed'
            time.sleep(2)
            self.tickerdownloadbutton.button_type = 'default'
            self.tickerdownloadbutton.label = 'press to download'
            return
        elif not s.empty:
            self.tickerdownloadbutton.button_type = 'success'
            self.tickerdownloadbutton.label = 'downloaded'
            time.sleep(2)
            self.tickerdownloader.value = ''
            self.tickerdownloadbutton.button_type = 'default'
            self.tickerdownloadbutton.label = 'press to download'
        self.update()

    def nix(self, val, lst):
        return [x for x in lst if x != val]

    def download_from_ibs(self, symbol_to_download, venue='SMART', ccy='USD'):

        print('called')

        def onError(reqId, errorCode, errorString, contract):
            print("ERROR", reqId, errorCode, errorString)
            if "fundamentals" in errorString:
                self.tickerdownloadbutton.button_type = 'danger'
                self.tickerdownloadbutton.label = 'funda data unavail'
                time.sleep(2)
                self.tickerdownloadbutton.button_type = 'default'
                self.tickerdownloadbutton.label = 'press to download'
                time.sleep(1)
                ib.disconnect()
                return
            if "ambiguous" in errorString:
                self.tickerdownloadbutton.button_type = 'danger'
                self.tickerdownloadbutton.label = 'ambigous symbol'
                time.sleep(2)
                self.tickerdownloadbutton.button_type = 'default'
                self.tickerdownloadbutton.label = 'press to download'
                ib.disconnect()
                return
            elif not any(ext in errorString for ext in ['HMDS', 'OK', 'ushmds']):
                self.tickerdownloadbutton.button_type = 'danger'
                self.tickerdownloadbutton.label = 'general error'
                time.sleep(2)
                self.tickerdownloadbutton.button_type = 'default'
                self.tickerdownloadbutton.label = 'press to download'
                ib.disconnect()


        ib = IB()
        ib.errorEvent += onError
        #ib.setCallback('error', onError)
        util.patchAsyncio()

        print('not connected...trying to connect')
        if not ib.isConnected():
            print("Connecting to:", ib_server, ib_port)
            ib.connect(ib_server, ib_port, clientId=25)

        contract1 = Stock(symbol_to_download, venue, ccy)
        try:
            timeout = 10
            req = ib.reqHistoricalDataAsync(contract1, endDateTime='', durationStr=duration,
                                     barSizeSetting=barSizeSetting, whatToShow='TRADES', useRTH=True)
            bars1=ib.run(asyncio.wait_for(req, timeout))
        except (asyncio.TimeoutError):
            print("TimeOuterror caught")
            ib.disconnect()
            return pd.DataFrame()

        if contract1.symbol not in self.catalog.STOCK:
            try:
                print("trying to get FUNDA")
                fundamentals = ib.reqFundamentalData(contract1, 'ReportSnapshot')
            except:
                #2018-11-21 01:04:30,468 Error 430, reqId 4: We are sorry, but fundamentals data for the security specified is not available.failed to fetch, contract: Stock(symbol='PSCT', exchange='SMART', currency='USD')
                #ERROR 4 430 We are sorry, but fundamentals data for the security specified is not available.failed to fetch
                print("Some error happened when attemping to get fundamental data")
                return
            soup = BeautifulSoup(fundamentals, 'xml')
            CompanyName = soup.find('CoID', Type='CompanyName').contents[0]
            Industry = soup.find('Industry').contents[0]
            ebitda = soup.find('Ratio', FieldName='TTMEBITD').string
            marketcap = soup.find('Ratio', FieldName='MKTCAP').string
            catalog_line = pd.DataFrame([[contract1.symbol, CompanyName, Industry, marketcap, ebitda]],
                                        columns=['STOCK', 'COMPANY', 'INDUSTRY', 'MARKETCAP', 'EBIDTA'])
            self.catalog = self.catalog.append(catalog_line, ignore_index=True)
            self.catalog.to_csv(catalog_file)

        ib.disconnect()

        df0 = util.df(bars1)
        df0 = pd.DataFrame(df0)
        if df0.empty:
            print("df0 is empty!!!")
            return df0

        dp0 = self.history_dir + symbol_to_download + '.csv'
        try:
            os.remove(dp0)
        except OSError:
            pass
        df0.to_csv(dp0)
        df0 = pd.read_csv(self.history_dir + symbol_to_download + '.csv',
                          index_col='date',
                          usecols=[1, 2, 3, 4, 5, 6], parse_dates=True)

        time.sleep(1)

        return df0


    def update(self, selected=None):
        print("UPDATE CALLED")
        self.option_diagram.update(self.all_stocks_data)


gemini=Gemini()
