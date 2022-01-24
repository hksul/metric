import streamlit as st
import requests

apiKey = st.secrets.db_credentials.apiKey
apiUrl = st.secrets.db_credentials.apiUrl
apiId = st.secrets.db_credentials.apiId

def getData(action):
     url2 = apiUrl % ( action, apiKey, apiId)
     result = requests.get(url2)
     return eval(result.text.strip())

balance = getData('getuserbalance')
hashrate = getData('getuserhashrate')

totBalance = sum(balance['getuserbalance']['data'].values())
curHashrate = hashrate['getuserhashrate']['data']

st.write(totBalance)
st.write(curHashrate)
