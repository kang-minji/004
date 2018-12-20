from flask import Flask, render_template, request
import requests
import json
import time
import os
from bs4 import BeautifulSoup as bs


app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_URL = 'https://api.hphk.io/telegram'

# '/telegram' 이라는 식으로 쉽게 챗봇을 설정해두면 해킹될 가능성이 있다.
@app.route('/{}'.format(TELEGRAM_TOKEN), methods=['POST'])
def telegram():
    # telegram으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드가 들어간다.
    
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
    msg = req["message"]["text"]
    
    if (req["message"]["text"] == "안녕"):
        msg = "첫만남에는 존댓말을 써야죠!"
    elif (req["message"]["text"] == "안녕하세요"):
        msg = "인사 자알~ 하신다."   

    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN)

    requests.get(url, params={"chat_id":chat_id, "text":msg})

    return '', 200
# 404, 500, 403 등의 숫자가 나타내는 것은 http status code를 뜻하며, 서버에 보낸 요청이 제대로 왔는지 등.

@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    
    params = {
        'url': 'https://ssafy-ohdi.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    response = requests.get(url, params = params).text
    return response


@app.route('/exchange')
def exchange():
    today=time.strftime('%a').lower()
    url = 'https://spot.wooribank.com/pot/jcc?withyou=CMCOM0184&__ID=c012238'
    params = {
        'BAS_DT_601': '20181219',
        'NTC_DIS': 'A',
        'INQ_DIS_601': '',
        'NTC_DIS': 'A',
        'SELECT_DATE_601': '2018.12.19',
        'SELECT_DATE_601Y': '2018',
        'SELECT_DATE_601M': '12',
        'SELECT_DATE_601D': '19'
    }
    
    # params는 맨 위의 페이지 url 에서 "?=" 이 뒤에 계속해서 변경되는 부분이다.
    
    response = requests.post(url, params).text
    print(response)
    soup = bs(response, 'html.parser')
    
    exchanges=[]
    
    
    li=soup.select('.tbl-type-1 tbody tr')
    url_base = 'https://spot.wooribank.com'
    rates = []
    
    # 해당 사례는 element 페이지에서는 알 수 없고, 
    # network 에서 class 를 찾고, 이를 어떤 형태로 이루어졌는지를 파악한다.
    # 해당 사례의 경우에는 tbl-type-1에서 tbody -> tr 순으로 이루어져 있고,
    # 최종적으로 td의 데이터에서 2번째, 3번째를 가져와야 하는 것을 알 수 있다.
    
    for item in li:
        rate = {
            'nation': item.select('td')[1].text,
            'rate': item.select('td')[2]
        }
        rates.append(rate)
    print(rates)
    return '{}'.format(rates)
    # fxprint > table > tbody > tr:nth-child(1) > td:nth-child(2)
    # <a href="/pot/Dream?withyou=CMCOM0184" class="ui-tab-selector"><span class="hidden ui-tab-current">현재 위치 </span><span class="ui-tab3-arrow">&nbsp;</span>일별환율조회</a>