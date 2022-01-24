

import requests
key = ''
url = ''
id = ''
actionList = ['getuserbalance', 'getuserhashrate']
def getData(action):
     url2 = url % ( action, key, id)
     result = requests.get(url2)
     return eval(result.text.strip())
balance = getData('getuserbalance')
hashrate = getData('getuserhashrate')
sum(balance['getuserbalance']['data'].values())
hashrate['getuserhashrate']['data']
