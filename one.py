import streamlit as st
import streamlit.components.v1 as components
from typing import List
from httpx import Client
import hashlib
import datetime
import calendar
import requests
import re
from urllib.parse import urljoin, urlparse
import json

class Authentication:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.current_time = datetime.datetime.utcnow()
        self.timestamp = calendar.timegm(self.current_time.utctimetuple())

    def signature(self, payload: str) -> str:
        payload = json.dumps(payload)
        signature = f"{self.app_id}{self.timestamp}{payload}{self.app_secret}"
        hashing = hashlib.sha256(signature.encode("utf-8"))
        return hashing.hexdigest()
    
class ShortLink:
    def __init__(self, origin_url: str, sub_ids: List[str] = []):
        self.origin_url = self._clean_url(origin_url)
        self.sub_ids = sub_ids

    @property
    def payload(self):
        graphql_query = """mutation{{
            generateShortLink(input: {{
                originUrl: "{}",
                subIds: {}
            }}){{
                shortLink
            }}
        }}""".format(
            self.origin_url, json.dumps(self.sub_ids)
        )
        query_payload = {"query": graphql_query}
        return query_payload

    def _clean_url(self, url):
        clean_url = urljoin(url, urlparse(url).path)
        return clean_url

class ShopeeClient:
    base_url = "https://open-api.affiliate.shopee.vn"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._client = Client(base_url=self.base_url)

    def post(self, payload: str):
        headers = self._headers(payload)
        return self._client.post("/graphql", headers=headers, json=payload)

    def _headers(self, payload):
        auth = Authentication(self.app_id, self.app_secret)
        headers = {
            "Authorization": f"SHA256 Credential={auth.app_id}, Signature={auth.signature(payload)}, Timestamp={auth.timestamp}",
            "Content-Type": "application/json",
        }
        return headers


class ShopeeAffiliate:
    def __init__(self, app_id: str, app_secret: str):
        self._client = ShopeeClient(app_id=app_id, app_secret=app_secret)

    def shortlink(self, origin_url: str, sub_ids: List[str] = []):
        link = ShortLink(origin_url=origin_url, sub_ids=sub_ids)
        resp = self._client.post(payload=link.payload)
        return resp
APP_ID = "17398250011"
APP_SECRET = "U675F3TO44TAWI67LJBUZBZN44QVSJKD"

#url = "https://shopee.vn/D%E1%BA%A7u-%C4%83n-Neptune-Light-5L-i.137264191.5746396694"
#sub_ids = []

client = ShopeeAffiliate(app_id=APP_ID, app_secret=APP_SECRET)
#print(json.loads(resp.text)["data"]["generateShortLink"]["shortLink"])

#title
st.image("avata.png",width=150)
st.title("KOL PhanChau")

user = st.text_input("Nhập username shopee của bạn vào đây!")
url = st.text_input("Nhập link sản phẩm của bạn vào đây!")
#button submit
#try:
if st.button("Lấy link"):
    if len(user) > 31:
        user="none"
    resp = client.shortlink(url, [user])
    link = json.loads(resp.text)["data"]["generateShortLink"]["shortLink"]
    id = re.findall(r'\d+', url.split('?')[0])[-2:]
    try:
        sc = requests.get(f"https://shopee.vn/api/v4/item/get?itemid={id[1]}&shopid={id[0]}").json()
        name = sc["data"]["name"]
        img = sc["data"]["image"]
        price = int(sc["data"]["price_min"])/100000
    except:
        name = "không thể tải tên sản phẩm"
        img = "https://cf.shopee.vn/file/e6a3b7beffa95ca492926978d5235f79"
        price = "00000"
    html_string = f'''
    <link rel="stylesheet" href="https://gartic.ml/style.css">
    <link rel="stylesheet" href="https://odindesignthemes.com/vikinger-theme/wp-content/themes/vikinger/sass/_form.scss">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <style> 
    button {{
                background-color: #23d2e2;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;border-radius: 10px
    }}
    </style>
    
    <div class="section-filters-bar v2" style="background: #fff;"><div class="section-filters-bar-actions full"><div class="form"><div class="form-row split"><div class="form-item"><div class="form-input small with-button active"><input type="text" value="{link.replace('https://', '')}" id="find" readonly="readonly" style="border: 1px solid #dedeea;"><button onclick="copy()" class="button primary" style="background: #4b9bff;width: 40%;line-height: 20px">sao chép</button></div></div>
</div></div></div>
<div id="item" class="grid grid-4-4-4 centered" style="background: #cdcdcd;border-radius: 12px;"><a href="{link}"> 
<div class="badge-item-preview">
        <img class="badge-item-preview-image" style="border-radius: 5px;" src="https://cf.shopee.vn/file/{img}" alt="badge-gold-b">
        <div class="badge-item-preview-info" href="{link}">
          <p class="badge-item-preview-title">{name}</p>
          <p class="badge-item-preview-timestamp">{price}đ</p>
          <p class="badge-item-preview-text">{link}</p>
        </div>
      </div>
      </a></div></div>
    <script>
    function copy() {{
        var $temp = $("<input>");
          $("body").append($temp);
          $temp.val("{link}").select();
          document.execCommand("copy");
          $temp.remove();
    }}
    </script>
    '''
    components.html(html_string, height=300) 
    st.markdown('<p style="font-family:sans-serif; color:red; font-size: 20px;">Cảm ơn bạn đã ủng hộ!</p>', unsafe_allow_html=True)
#except:
 #   st.markdown('<p style="font-family:sans-serif; color:red; font-size: 20px;">lỗi hệ thống!</p>', unsafe_allow_html=True)