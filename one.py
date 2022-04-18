import streamlit as st
import streamlit.components.v1 as components
from typing import List
from httpx import Client
import hashlib
import datetime
import calendar
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
sub_ids = ["python"]

client = ShopeeAffiliate(app_id=APP_ID, app_secret=APP_SECRET)
#print(json.loads(resp.text)["data"]["generateShortLink"]["shortLink"])

#title
st.title("KOL shopee")

url = st.text_input("Nhập link sản phẩm của bạn vào đây!")
#button submit
#try:
if st.button("Lấy link"):
    resp = client.shortlink(url, sub_ids)
    link = json.loads(resp.text)["data"]["generateShortLink"]["shortLink"]

    html_string = f'''
    <link rel="stylesheet" href="https://odindesignthemes.com/vikinger-theme/wp-content/themes/vikinger/style.css">
    <link rel="stylesheet" href="https://odindesignthemes.com/vikinger-theme/wp-content/themes/vikinger/sass/_form.scss">
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
    <div class="section-filters-bar v2" style="background: #fff;"><div class="section-filters-bar-actions full"><div class="form"><div class="form-row split"><div class="form-item"><div class="form-input small with-button active"><input type="text" value="{link}" id="find" style="border: 1px solid #dedeea;"><button onclick="findit()" class="button primary" style="background: #4b9bff;width: 40%;line-height: 20px">sao chép</button></div></div>
</div></div></div>
<div id="item" class="grid grid-4-4-4 centered" style="background: #f3f3f3;border-radius: 12px;"><a href="undefined"> 
<div class="badge-item-preview">
        <img class="badge-item-preview-image" src="https://cf.shopee.vn/file/0e8a2bf1747247a92f4f5dde480364d9_tn" alt="badge-gold-b">
        <div class="badge-item-preview-info" href="https://shopee.vn/product/393363168/10276471405">
          <p class="badge-item-preview-title">quần jean</p>
          <p class="badge-item-preview-timestamp">19.000đ</p>
          <p class="badge-item-preview-text">đã bán undefined sp</p>
        </div>
      </div>
      </a></div></div>
    <button id="bbb">{link}</button>
    <button onclick="myFunction()">Sao chép</button>
    <script>
    function myFunction() {{
    var elem = document.getElementById('bbb');
    var txt = elem.textContent || elem.innerText;
    navigator.clipboard.writeText(txt);
    }}
    </script>
    '''
    components.html(html_string, height=300) 
    st.text("Link đã được tạo thành công!")
    st.text("Bạn có thể sao chép link hoặc nhấp vào link để mua hàng!")
    st.text("Khi đơn hàng hoàn thành mình sẽ gửi 1000xu đến tài khoản mua hàng!")
    st.markdown('<p style="font-family:sans-serif; color:red; font-size: 20px;">Cảm ơn bạn đã ủng hộ!</p>', unsafe_allow_html=True)
#except:
 #   st.markdown('<p style="font-family:sans-serif; color:red; font-size: 20px;">lỗi hệ thống!</p>', unsafe_allow_html=True)