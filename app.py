from flask import Flask, render_template, request
import requests
import json
import time
import os
from bs4 import BeautifulSoup as bs
import time


app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_URL = 'https://api.hphk.io/telegram'

CAFE_LIST = {
    '전체': -1,
    '부천점': 15,
    '안양점': 13,
    '대구동성로2호점':14,
    '대구동성로점':9,
    '궁동직영점':1,
    '은행직영점':2,
    '부산서면점':19,
    '홍대상수점':20,
    '강남점':16,
    '건대점':10,
    '홍대점':11,
    '신촌점':6,
    '잠실점':21,
    '부평점':17,
    '익산점':12,
    '전주고사점':8,
    '천안신부점':18,
    '천안점':3,
    '천안두정점':7,
    '청주점':4
}    

# '/telegram' 이라는 식으로 쉽게 챗봇을 설정해두면 해킹될 가능성이 있다.
@app.route('/{}'.format(TELEGRAM_TOKEN), methods=['POST'])
def telegram():
    # telegram으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드가 들어간다.
    
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
    msg = ''
    txt = req["message"]["text"]

    if(txt.startswith('마스터키')):
        cafe_name = txt.split(' ')[1]
        cd = CAFE_LIST[cafe_name]
        if(cd>0):
            data=masterkey_info(cd)
            
        else:
            data=masterkey_list()
            
        msg = []
        for d in data:
            msg.append('\n'.join(d.values()))
        msg = '\n'.join(msg)
        
    elif(txt.startswith('서울이스케이프')):
        cafe_name = txt.split(' ')
        
        if(len(cafe_name)>2):
            cafe_name = cafe_name[1] + ' ' + cafe_name[2]
        else:
            cafe_name = cafe_name[-1]
            if(cafe_name == "전체"):
                msg = seoul_escape_list()
            else:
                msg = seoul_escape_info(cafe_name)
                
        msg = '\n'.join(msg)           
                
    else:
        msg = '등록되지 않은 지점입니다.'

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

    url = 'https://spot.wooribank.com/pot/jcc?withyou=CMCOM0184&__ID=c012238'
    params = {
        'BAS_DT_601': '20181219',
        'NTC_DIS': 'A',
        'INQ_DIS_601': '',
        'SELECT_DATE_601': '2018.12.19',
        'SELECT_DATE_601Y': '2018',
        'SELECT_DATE_601M': '12',
        'SELECT_DATE_601D': '19'
    }
    
    # params는 맨 위의 페이지 url 에서 "?=" 이 뒤에 계속해서 변경되는 부분이다.
    
    response = requests.post(url, params).text
    print(response)
    soup = bs(response, 'html.parser')
    
    li=soup.select('.tbl-type-1 tbody tr')
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
    
def masterkey_list():
        
    url = "http://www.master-key.co.kr/home/office"
    
    response = requests.get(url).text
    
    document = bs(response, 'html.parser')
    
    # ul = document.select('.escape_list')
    # 별명이 class이면 . id 인 경우에는 # / 혹은 본명인 태그이름.
    # excape list로 시작하는 요소가 하나로 입력됨.
    
    lis = document.select('.escape_list .escape_view')
    # 각각의 요소로 입력됨 . len함수로 가져올 경우 개수가 늘어남.
    
    cafe_list = []
    # 카페 리스트라는 배열을 두고.
    
    for li in lis:
        # title 문자열에서 new를 빼고 싶다.
        # 검색 - python how to v(동사) eliminate string from string
        title = li.select_one('p').text
        if(title.endswith('NEW')):
            title = title[:-3]
            # 뒤에서 3개를 빼겠다.
            
        address = li.select('dd')[0].text
        tel = li.select('dd')[1].text
            # .text붙여야 tag 떼고 문자만 나옴.
        link = 'http://www.master-key.co.kr' + li.select_one('a')["href"]
            
        cafe = {
            'title': title,
            'tel': tel,
            'address': address,
            'link': link
        }
        
        cafe_list.append(cafe)
    return cafe_list
        
    #print(li.select_one('p').text)
    #print(li.select('dd'))
        # 주소, 전화번호를 긁어오겠다.
    #print(li.select_one('a'))
        # print(li.select_('a')[0]) - a로 묶여있는 많은 정보중에 첫번째 부분만 가져오겠다.


# 예약 정보를 가지고 오기
# 페이지 소스 보기로는 알 수 없다.
# 검사의 network 페이지에 들어가고, 예약 날짜를 바꾸면 booking list new 이런식으로 새롭게 바뀐 내용을 볼 수 있다.
# 이곳에서 가장 바깥에서 가지고 올 수 있는 것을 검색하고, 그 안쪽으로 검색하면 된다. (개수를 맞게 가져올 수 있음)

# <ul class='reserve'>가 가장 바깥, <li class='escape_view'>가 필요한 정보 하나하나.

def masterkey_info(cafe_cd):

    url = "http://www.master-key.co.kr/booking/booking_list_new"
    params = {
        'date': time.strftime("%Y-%m-%d"), 
        'store': cafe_cd,
        'room': ''
    }
# 날짜가 url 에 안적혀 있음.
# method가 post / requests.get은 request body의 params에 숨겨있다.
# 맨 밑에 form data 부분에 있는 것을 params에 붙여준다.

    response = requests.post(url, params).text
    document = bs(response, 'html.parser')
    # ul = document.select('.reserve')
    
    lis = document.select('.reserve .escape_view')
    
    theme_list = []
    
    for li in lis:
        title = li.select('p')[0].text
        info = ''
        for col in li.select('.col'):
            info = info + '{} - {}\n'.format(col.select_one('.time').text, col.select_one('.state').text)
        theme = {
            'title' : title,
            'info' : info
        }
        theme_list.append(theme)
        
    return theme_list

def get_total_info():

    url = 'http://www.seoul-escape.com/reservation/change_date/'
    params = {
        'current_date' : '2018/12/21'
    }
    
    response = requests.get(url, params = params).text
    document = json.loads(response)
    cafe_code = {
        '강남1호점': 3,
        '홍대1호점': 1,
        '부산 서면점': 5,
        '인천 부평점': 4,
        '강남2호점': 11,
        '홍대2호점': 10
    }
    total = {}
    game_room_list = document["gameRoomList"]
    for cafe in cafe_code:
        total[cafe]=[]
        for room in game_room_list:
            if(cafe_code[cafe] == room["branch_id"]):
                total[cafe].append({"title":room["room_name"], "info":[]})
    
    book_list = document["bookList"]
    
    for cafe in total:
        for book in book_list:
            if(cafe==book["branch"]):
                for theme in total[cafe]:
                    if(theme["title"] == book["room"]):
                        if(book["booked"]):
                            booked = "예약완료"
                        else:
                            booked = "예약가능"
    
                        theme["info"].append('{} - {}'.format(book["hour"], booked))
    
    return(total)
    
def seoul_escape_list():
    total = get_total_info()
    
    return total.keys()
    
def seoul_escape_info(cd):
    total = get_total_info()
    cafe = total[cd]
    tmp = []
    for theme in cafe:
        tmp.append("{}\n {}".format(theme["title"], '\n'.join(theme["info"])))
    return tmp
    
