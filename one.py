import streamlit as st
import requests
import random
import requests
import json

ip = requests.get('https://checkip.amazonaws.com').text.strip()

st.title(ip)

def create_group(SPC_EC, userid):
  return requests.post("https://giaitri.shopee.vn/gc-api/desktop-app-api/lottery/create-group/", headers={'Content-Type': 'application/json; charset=UTF-8', 'Cookie': f'SPC_EC={SPC_EC}; SPC_U={userid}'}).json()["data"]["group_id"]

def join_group(SPC_EC, userid, group_id):
  try:
    body = {"group_id":group_id}
    requests.post("https://giaitri.shopee.vn/gc-api/desktop-app-api/lottery/join-group/", data=json.dumps(body), headers={'Content-Type': 'application/json; charset=UTF-8', 'Cookie': f'SPC_EC={SPC_EC}; SPC_U={userid}'}).json()
  except:
    pass
  return "sucess"

user = requests.get("https://627729c02f94a1d7060a6bbc.mockapi.io/user").json()
random.shuffle(user)
grid = 0
while grid == 0:
  item = user.pop(0)
  try:
    st.text(item["username"])
    grid = create_group(item["SPC_EC"], item["userid"])
  except:
    pass    

for i in user:
  msg = join_group(i["SPC_EC"], i["userid"], grid)
  if msg == 122:
    try:
      grid = create_group(i)
    except:
      pass
