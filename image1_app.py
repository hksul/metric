# -*- coding: utf-8 -*-
"""Metric Studio Replication Image 1

"""
#!pip install -U finance-datareader

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import FinanceDataReader as fdr
import pymongo
import time

@st.cache
def downloadRawData(dType):
  if dType == 'KOSPI':
    df = fdr.DataReader('KS11', 2000)
  elif dType == 'KOSDAQ':
    df = fdr.DataReader('KQ11', 2000)  
  return df
  

def processImage1(dType, sDate, eDate):
  df = downloadRawData(dType)
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
    new_row = {'days':dateDiff, 'win %':numWin/numTot*100}
    df_result = df_result.append(new_row, ignore_index=True)
  return df_result

def connect_db(databaseName):    
    mUri = "mongodb://%s:%s@%s" % (st.secrets.db_credentials.username, st.secrets.db_credentials.password, st.secrets.db_credentials.uriString)
    client = pymongo.MongoClient(mUri)
    db = client[databaseName]
    return db
                                
def processAndInsertToDB(dataType, startDate, endDate):
    df_result = processImage1(dataType, startDate, endDate)
    data_dict = df_result.to_dict("records")
    company.insert_one({"index":"image1_%s_%s_%s" % (dataType, startDate.year, endDate.year),"data":data_dict})
    return df_result

def fetchFromDB(dataType, startDate, endDate):

    data_from_db = company.find_one({"index":"image1_%s_%s_%s" % (dataType, startDate.year, endDate.year)})
    df = pd.DataFrame(data_from_db["data"])
    return df

def drawImage(df_res, dataType, startDate, endDate):
    fig1, ax = plt.subplots()
    x = [int(a) for a in list(df_res['days'])]
    xi = list(range(len(x)))
    y = list(df_res['win %'])
    ax.plot(xi, y, color='b')
    ax.set_xlabel('Timeframe - days')
    ax.set_ylabel('Probability (%)') 
    ax.set_title('Positive Return Probability for Korean Stocks - %s Index; %s - %s' % (dataType, startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')))
    ax.set_xticks(ticks=xi)
    ax.set_xticklabels(x)
    st.pyplot(fig1)

    

db = connect_db("metricStudio")
company = db["image1"]

dataTypeTmp = st.sidebar.selectbox("Market", ('KOSDAQ Index', 'KOSPI Index'))
dataType = dataTypeTmp[:-6]

startY = st.sidebar.selectbox("Start Year", range(2000, 2011))
startDate = datetime.date(startY, 1, 1)

today = datetime.datetime.now()
endY = st.sidebar.selectbox("End Year", range(2011, today.year))
endDate = datetime.date(endY, 12, 31)


if dataType or startY or endY:
  with st.spinner('Processing...'):
    #st.write("Update Database running")
    try:
      df_r = fetchFromDB(dataType, startDate, endDate)
    except:
      df_r = processAndInsertToDB(dataType, startDate, endDate)    
    drawImage(df_r, dataType, startDate, endDate)


#if st.sidebar.button('Update All'):
#  with st.spinner('Processing...'):
#    for dataType in ('KOSDAQ Index', 'KOSPI Index'):
#      for endYear in range(2011, today.year):
#        endDate = datetime.date(endYear, 12, 31)
#        try:
#          df_r = fetchFromDB(dataType, startDate, endDate)
#        except:
#          df_r = processAndInsertToDB(dataType, startDate, endDate)    
#        drawImage(df_r, dataType, startDate, endDate)
#        time.sleep(30)

