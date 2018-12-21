from bs4 import BeautifulSoup as bs
import requests



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
        'date': '2018-12-22', 
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
    info = ''
    for li in lis:
        title = li.select('p')[0].text
        for col in li.select('.col'):
            info = info + '{} - {}\n'.format(col.select_one('.time').text, col.select_one('.state').text)
        theme = {
            'title' : title,
            'info' : info
        }
        theme_list.append(theme)
        
    return theme_list
    
    
# msg.split(' ')[1]
# print(masterkey_info(21))

# 사용자로부터 '마스터키 *** 점'이라는 메시지를 받으면
# 해당 지점에 대한 오늘의 정보를 요청하고(크롤링)
# 메시지(예약정보)를 보내준다.

#for cafe in masterkey_list():
#    print(cafe["link"].split('=')[1])
#    print('{}:{}'.format(cafe["title"],cafe["link"].split('=')[1]))    

# 위의 정보를 그대로 딕셔너리에 넣어버림.


print(cafe_list['전체'])
