from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime

hotNews = []
hotNewsUpdateTime = datetime.now()

def bad_request_param_response():
    response = {}
    response["content"] = {}
    response["status"] = 1
    response["message"] = "请求参数错误"
    response["code"] = 500
    return JsonResponse(response)


def standard_response(resDict, code=200, status=0, message='success'):
    response = {}
    response["content"] = resDict
    response["status"] = status
    response["message"] = message
    response["code"] = code
    print(response)
    return JsonResponse(response)

def hello(request):
    return HttpResponse("Hello world ! ")

def get_BaiduHotNews(request):
    global hotNewsUpdateTime
    global hotNews
    nowTime = datetime.now()
    inter = nowTime - hotNewsUpdateTime
    if inter.seconds > 60*10 or len(hotNews) == 0:
        print('获取百度热点')
        url = 'https://top.baidu.com/board?tab=realtime'
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/60.0.3112.113 Safari/537.36',
            'accept': 'application/json, text/plain, */*'}
        html = get_html(url, headers)
        hotNews = get_pages(html)
        hotNewsUpdateTime = datetime.now()
    if len(hotNews) >= 10:
        return standard_response({'result': hotNews[0:10]})
    else:
        return standard_response({'result': ['热点获取失败']})

def get_html(url,headers):
    r = requests.get(url,headers=headers)
    r.encoding = r.apparent_encoding
    return r.text

def checkClassName(obj, startText):
    ret = False
    if 'class' in obj.attrs:
        keys = obj['class']
        if len(keys) > 0 and keys[0].startswith(startText):
            ret = True
    return ret


def get_pages(html):
    #global s
    #with open('baidu.html','w',encoding='utf-8') as f:
    #    f.write(html)
    soup = BeautifulSoup(html,'html.parser')
    #print (soup.prettify())
    all_topics=soup.find_all('div')
    #test = soup.find('ul',class_='s-news-rank-content')
    #print(test)
    all = []
    for each_topic in all_topics:
        if checkClassName(each_topic,'category-wrap'):
            allDiv = each_topic.find_all('div')
            for eachTitle in allDiv:
                if checkClassName(eachTitle,'content'):
                    allTitle = eachTitle.find_all('a')
                    for item in allTitle:
                        if checkClassName(item,'title'):
                            all.append(item.contents[0].string.strip())
    return all