# -- coding: utf-8 -
from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

from myEPD.models import hotNewsTable
from testdjango.celery import app

hotNews = []
hotNewsUpdateTime = datetime.now()

def bad_request_param_response():
    response = {}
    response["result"] = {}
    response["status"] = 1
    response["message"] = "请求参数错误"
    response["code"] = 500
    return JsonResponse(response)


def standard_response(code=200, status=0, message='success', resDict={}, result=True):
    response = {}
    response["datas"] = resDict
    response["result"] = result
    response["status"] = status
    response["message"] = message
    response["code"] = code
    print(response)
    return JsonResponse(response)

def get_request_body(request):
    try:
        data = json.loads(request.body)
    except Exception as e:
        data = {}
        print(e)
    return data

def hello(request):
    return HttpResponse("Hello world ! ")

def get_BaiduHotNews(request):
    global hotNewsUpdateTime
    global hotNews
    hotNews.clear()
    query = hotNewsTable.objects.all()
    for item in query:
        hotNews.append(item.title)
    if len(hotNews) < 10:
        print('获取百度热点')
        update_hotNews()
    if len(hotNews) >= 10:
        return standard_response(result=hotNews)
    else:
        return standard_response(result=['热点获取失败'])

def update_hotNews():
    global hotNewsUpdateTime
    global hotNews
    url = 'https://top.baidu.com/board?tab=realtime'
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/60.0.3112.113 Safari/537.36',
        'accept': 'application/json, text/plain, */*'}
    html = get_html(url, headers)
    hotNews = get_pages(html)
    hotNewsUpdateTime = datetime.now()
    hotNewsTable.objects.all().delete()
    for item in hotNews:
        hot = hotNewsTable()
        hot.title = item
        hot.save()

def get_html(url,headers):
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    return r.text

def checkClassName(obj, startText):
    ret = False
    if 'class' in obj.attrs:
        keys = obj['class']
        if len(keys) > 0 and keys[0].startswith(startText):
            ret = True
    return ret

def get_weather(request):
    cityId = request.GET.get('citykey')
    url = 'http://wthrcdn.etouch.cn/weather_mini?citykey=%s' % cityId
    r = requests.get(url)
    text = r.text
    result = json.loads(text)
    print(result)
    return JsonResponse(result)


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

@app.task(bind=True)
def debug_task(self):
    print('hello')

@app.task(bind=True)
def updateHotNews_task(self):
    print('update hotnews task start')
    update_hotNews()
