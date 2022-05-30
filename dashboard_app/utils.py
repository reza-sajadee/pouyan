import requests
import json
import pandas as pd
#from khayyam import *

import os
from numpy import inf

#import matplotlib.pyplot as plt
#from bidi.algorithm import get_display
#import arabic_reshaper

#from os import path
import numpy as np

from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import delta, gamma , vega , theta , rho
#from scipy.stats import norm
#import pytse_client as tse
from math import log, sqrt, pi, exp
#from scipy.stats import norm
#from datetime import datetime, date
#pd.options.mode.chained_assignment = None  # default='warn'
from pandas import DataFrame
#from py_vollib.black_scholes import black_scholes as bs
#from py_vollib.black_scholes.greeks.analytical import delta, gamma , vega , theta , rho
#import opstrat as op
#from khayyam import *
import pytse_client as tse

def create_dataFrame ():
    url = 'https://tse.ir/json/MarketWatch/data_7.json?1639550350064?1639550350064'
    response = requests.get(url, verify=False)
    columns = []
    values = []
    response_dict = json.loads(response.text.encode().decode('utf-8-sig'))
    call_values = []
    put_values = []
    raw_datas = response_dict['bData']
    for raw_data in raw_datas:
        i=0
        x1 = raw_data
        x2 = raw_data['val']
        val = []
        if raw_data['darayi'] == 'ص.دارا':
            val.append('wnvh')
        if raw_data['darayi'] == 'ص.دارا' or raw_data['darayi'] == 'های' or len( raw_data['darayi']) <4 or '.' in raw_data['darayi'] :
            continue
        val.append(raw_data['darayi'])
        for j in range(len(x2)):
            val.append(x2[j]['v'])
        val.append(raw_data['darayi'])
        call_values.append(val[0:17])
        put_values.append(val[13:])
    dfcall = pd.DataFrame()
    dfputt = pd.DataFrame()
    dfcall = pd.DataFrame(call_values , columns=['دارایی پایه','نماد' ,'نام','قیمت تسویه امروز','موقعیت های باز',
                                     'حجم','ازرش معاملات','دفعات معامله','آخرین قیمت ',
                                     'بهترین سفارش فروش حجم','بهترین سفارش فروش قیمت','بهترین سفارش خرید قیمت','بهترین سفارش خرید حجم ',
                                     'اندازه قرارداد','روز های باقی مانده','قیمت اعمال','قیمت مبنای دارایی پایه' ])    





    dfputt = pd.DataFrame(put_values , columns=[
                                         'اندازه قرارداد','روز های باقی مانده','قیمت اعمال','قیمت مبنای دارایی پایه',
                                         'بهترین سفارش فروش حجم','بهترین سفارش فروش قیمت','بهترین سفارش خرید قیمت','بهترین سفارش خرید حجم',
                                         'آخرین قیمت ','دفعات معامله','ارزش معاملات','حجم',
                                         'موقعیت های باز','قیمت تسویه امروز','نام','نماد' , 'دارایی پایه' ] )    
    
    dfcall = dfcall.reset_index(drop=True)
    dfputt = dfputt.reset_index(drop=True)
    last_update = response_dict['time']['hour'] + ':' +response_dict['time']['min'] + ':' + response_dict['time']['sec']
    return dfcall , dfputt ,last_update



def convert_to_float(df_raw):
    for col in df_raw.columns:
        if(col == 'دارایی پایه' or col == 'نماد'or col == 'نام'):
           
            continue
        if(col == 'ازرش معاملات' or col == 'sdt'):
            
            continue
            #if(raw_call_dfs[col].str.contains('B')):
        try:
            
            df_raw[col] = df_raw[col].str.replace(',','').astype({col:float})
            
        except:
            
            continue
    df_raw = df_raw.reset_index(drop=True)
    return df_raw




def calc_sigma(df):
    sigma = pd.DataFrame()
    namads = []
    for namad in list(df['دارایی پایه'].unique()):
        namads.append(namad.replace('ي' , 'ی').replace('ك','ک'))
    
    
    tickers = tse.download(symbols=namads, write_to_csv=False)
    temp_dict = {}
    for ticker in tickers:
        
        df2 = pd.DataFrame()
        df2 = tickers[ticker]
        df2 = df2.sort_index(axis=0,ascending=False)
        df2 = df2[:300]
        df2['return'] =  tickers[ticker]['adjClose'].pct_change(1)
        df2 = df2[1:]
        temp_dict[ticker] = np.sqrt(252) * df2['return'].std()
            
    sigma = sigma.append(temp_dict , ignore_index=True)
            
    return sigma
    
def blackScholes(r,S,K,T,sigma,type="c"):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    try:
        if(type=="c"):
            price = S*norm.cdf(d1,0,1) - K*np.exp(-r*T)*norm.cdf(d2,0,1)
            
        return price 
    except:
        print("something was werang")
        
def calc_call(raw_call_dfs):
    ir = 0.2
    df_dr = pd.DataFrame()
    
   
    
    raw_call_dfs['قیمت اعمال تنزیلی'] = raw_call_dfs['قیمت اعمال']/((1+ir * (raw_call_dfs['روز های باقی مانده'])/365))
    raw_call_dfs['هزینه اعمال مطمئن'] = raw_call_dfs['بهترین سفارش فروش قیمت'] + raw_call_dfs['قیمت اعمال تنزیلی']

    raw_call_dfs['قیمت بازار']= raw_call_dfs['بهترین سفارش فروش قیمت']
    raw_call_dfs['قیمت سهم پایه'] = raw_call_dfs['قیمت مبنای دارایی پایه']
    raw_call_dfs['سر به سر']  = (raw_call_dfs['هزینه اعمال مطمئن'] / raw_call_dfs['قیمت سهم پایه']) - 1
    raw_call_dfs['بی تفاوتی'] = (raw_call_dfs['قیمت اعمال تنزیلی'] /(raw_call_dfs['قیمت سهم پایه']- raw_call_dfs['بهترین سفارش فروش قیمت']) ) - 1
    raw_call_dfs['اهرم'] = raw_call_dfs['قیمت اعمال تنزیلی']/raw_call_dfs['بهترین سفارش فروش قیمت'] 
    raw_call_dfs['معیار'] = np.log(raw_call_dfs['اهرم']/10)*np.log(raw_call_dfs['حجم']*10)
    df_dr['دارایی پایه'] = raw_call_dfs['دارایی پایه']
    df_dr['نماد'] = raw_call_dfs['نماد']
    df_dr['روز های باقی مانده'] = raw_call_dfs['روز های باقی مانده']
    df_dr['قیمت مبنای دارایی پایه'] = raw_call_dfs['قیمت مبنای دارایی پایه']
    df_dr['قیمت اعمال'] = raw_call_dfs['قیمت اعمال']
    df_dr['قیمت تسویه امروز'] = raw_call_dfs['قیمت تسویه امروز']
   
    
    df_dr['قیمت اعمال تنزیلی'] = raw_call_dfs['قیمت اعمال تنزیلی']
    df_dr['هزینه اعمال مطمئن'] = raw_call_dfs['هزینه اعمال مطمئن']
    df_dr['قیمت بازار'] = raw_call_dfs['قیمت بازار']
    df_dr['سر به سر'] = raw_call_dfs['سر به سر']
    df_dr['بی تفاوتی'] = raw_call_dfs['بی تفاوتی']
    df_dr['اهرم'] = raw_call_dfs['اهرم']
    df_dr['معیار'] = raw_call_dfs['معیار']
    df_dr['sdt'] = np.nan
    sigma = calc_sigma(df_dr)
    for i in range(len(df_dr)):
        df_dr.at[i,'sdt'] = sigma[df_dr.at[i,'دارایی پایه'].replace('ي' , 'ی').replace('ك','ک')]
        
    df_dr['Delta'] = np.nan
    df_dr['BL'] = np.nan
    df_dr['d1'] = np.nan
    df_dr['d2'] = np.nan
    df_dr['Gamma'] = np.nan
    df_dr['Vega'] = np.nan
    df_dr['Theta'] = np.nan
    df_dr['Rho'] = np.nan
    for i in range(len(df_dr)):
        S = raw_call_dfs.at[i,'قیمت مبنای دارایی پایه']
        T = int(raw_call_dfs.at[i,'روز های باقی مانده'])/252
        sigma = df_dr.at[i,'sdt']
        K = raw_call_dfs.at[i,'قیمت اعمال']
        black = bs("c",S,K,T,ir,sigma)
        d1 = (np.log(S/K) + (ir + sigma**2/2)*T)/(sigma*np.sqrt(T))
        d2 = d1-sigma*np.sqrt(T)
        df_dr.at[i,'BL'] = black
        df_dr.at[i,'d1'] = d1
        df_dr.at[i,'d2'] = d2
        
        df_dr.at[i,'Delta'] = delta("c",S,K,T,ir,sigma)
        df_dr.at[i,'Gamma'] = gamma("c",S,K,T,ir,sigma)
        df_dr.at[i,'Vega']  = vega("c",S,K,T,ir,sigma)
        df_dr.at[i,'Theta']  = theta("c",S,K,T,ir,sigma)
        df_dr.at[i,'Rho']  = rho("c",S,K,T,ir,sigma)
    return df_dr
