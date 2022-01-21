# -*- coding: utf-8 -*-
"""Metric Studio Replication part 1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Yl8GOxB1heICQo_Lx8lQuEeF0YQWOvg6
"""

#!pip install -U finance-datareader

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import FinanceDataReader as fdr
import pymongo


def processImage1(dType, sDate, eDate):
  
  
  
  if dType == 'KOSPI':
    ks11_df = fdr.DataReader('KS11', sDate.year)
    df = ks11_df
  else:
    ks11_df = fdr.DataReader('KQ11', sDate.year)
    df = kq11_df

  df_result = pd.DataFrame()

  for dateDiff in (1, 5, 10, 15, 30, 60, 125):
    numLoss = 0
    numWin = 0
    numStalemate = 0
    for (index, row), ii in zip(df.iterrows(), range(len(df.index))):
      if index.date() <= eDate and index.date() >= sDate:
        if row['Close'] > df.iloc[ii-dateDiff]['Close']:
          numWin +=1
        elif row['Close'] < df.iloc[ii-dateDiff]['Close']:
          numLoss +=1
        else:
          numStalemate +=1
    numTot = numWin+numLoss+numStalemate
    #print(dateDiff, numWin/numTot, numLoss/numTot, numStalemate/numTot)
    new_row = {'days':dateDiff, 'win %':numWin/numTot*100}
    df_result = df_result.append(new_row, ignore_index=True)
  return df_result



def connect_db(databaseName):    
    mUri = "mongodb://%s:%s@%s" % (st.secrets.db_credentials.username, st.secrets.db_credentials.password, st.secrets.db_credentials.uriString)
    print(mUri)
    client = pymongo.MongoClient(mUri)
    db = client[databaseName]
    return db
                                 
startDate = datetime.date(2000, 1, 1)
today = datetime.datetime.now()
endDate = datetime.date(today.year, today.month, today.day)
print(endDate)
endDate = datetime.date(2014,12,31)
print(endDate)
dataType = 'KOSDAQ'
dataType = 'KOSPI'

                                 
                                 
db = connect_db("metricStudio")
company = db["image1"]

def processAndInsertToDB(dataType, startDate, endDate):
    df_result = processImage1(dataType, startDate, endDate)
    data_dict = df_result.to_dict("records")
    company.insert_one({"index":"image1_%s_%s_%s" % (dataType, startDate.year, endDate.year),"data":data_dict})
    return df_result

def fetchFromDB(dataType, startDate, endDate):

    data_from_db = company.find_one({"index":"image1_%s_%s_%s" % (dataType, startDate.year, endDate.year)})
    df = pd.DataFrame(data_from_db["data"])
    return df
                                 
                                 
country = st.sidebar.text_input('Country')

col1, col2, col3 = st.columns([1,1,1])

with col1:
    r1 = st.button('Update The Database')
with col2:
    r2 = st.button('2')
with col3:
    r3 = st.button('3')

if r1:
  st.write("Update Database running")

  #df_res = get_data(dataType)
  try:
    df_res = fetchFromDB(dataType, startDate, endDate)
  except:
    df_res = processAndInsertToDB(dataType, startDate, endDate)
    
  fig1, ax = plt.subplots()

  x = [int(a) for a in list(df_res['days'])]
  xi = list(range(len(x)))
  y = list(df_res['win %'])
  ax.plot(xi, y, color='b')
  ax.set_xlabel('Timeframe - days')
  ax.set_ylabel('Probability (%)') 
  ax.set_title('Positive Return Probability for Korean Stocks - %s; %s - %s' % (dataType, startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')))
  ax.set_xticks(ticks=xi)
  ax.set_xticklabels(x)
  #fig1.savefig('1.png')
  st.pyplot(fig1)
