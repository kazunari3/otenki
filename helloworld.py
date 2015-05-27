# coding: UTF-8
import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


import os
from google.appengine.ext.webapp import template

import urllib2
from BeautifulSoup import BeautifulSoup
import logging

import datetime
import locale
import time
from xml.dom import minidom
import simplejson
def str2float(str):
    try:
       return float(str)
    except:
       return 0.0
#気象庁のグラフ
highgraph = []
lowgraph = []
#WeaterHacksの今日の気温
todayhigh = []
todaylow = []
#WeaterHacksの明日の気温
tomorrowhigh = []
tomorrowlow = []

class MainPage(webapp.RequestHandler):
    def get(self):
         # 気象庁のURL
        url = 'http://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php'

        day = datetime.date.today()
         # 暫定で実行日の年と月の平均データを取得
        params = 'prec_no=46&block_no=47670&year=%d&month=%d&day=&view=p1' % (day.year,day.month)

        # paramsはhoge=1&fuga=2の形になっている
        f = urllib2.urlopen(url + '?' + params)
        html =  f.read()
     
         # サーバーから気象データのページを取得
        #html = urllib2.urlopen(f).read()
     
        soup = BeautifulSoup(html)
     
        trs = soup.find('table', { 'class' : 'data2_s' })
     
        del highgraph[:]
        del lowgraph[:]
        del todayhigh[:]
        del todaylow[:]
        del tomorrowhigh[:]
        del tomorrowlow[:]
         # 1レコードづつ処理する
        for tr in trs.findAll('tr')[4:]:
            tds = tr.findAll('td')
     
            if tds[1].string == None:   # その月がまだ終わってない場合、途中でデータがなくなる
                break;
     
            high = [0,0.0]
            low = [0,0.0]

            dic = {}
            #dic['day']              = str(tds[0].find('a').string)   # 日付
            d = datetime.date(day.year,day.month,int(tds[0].find('a').string))
            dic['day'] = int(time.mktime(d.timetuple())*1000)
            #dic['precipitation']    = str2float(tds[3].string.replace(')',''))       # 降水量
            dic['temperature.avg']  = str2float(tds[6].string.replace(')',''))       # 気温 - 平均
            dic['temperature.high'] = str2float(tds[7].string.replace(')',''))       # 気温 - 最高
            dic['temperature.low']  = str2float(tds[8].string.replace(')',''))       # 気温 - 最低
            #dic['sunshine duration']= str2float(tds[16].string.replace(')',''))      # 日照時間

            high[0] = dic['day']
            high[1] = dic['temperature.high']
            low[0] = dic['day']
            low[1] = dic['temperature.low']
            
            highgraph.append(high)
            lowgraph.append(low)


              # 最後に結果を表示する
            #for dic in list:
            #    logging.info('%s' % dic)

         #ここからはウェザーハックからの予報知取得処理
        src = urllib2.urlopen('http://weather.livedoor.com/forecast/webservice/json/v1?city=140010').read()
        logging.info('json = %s' % src)

        hacks_json = simplejson.loads(src)

        logging.info('title = %s' % hacks_json['title'])

        # celsiusタグの要素をすべて取得
        max = 0.0
        min = 0.0
        maxgraph=[0, 0.0]
        mingraph=[0, 0.0]

        try:
              # 明日の予報
            max = hacks_json['forecasts'][1]['temperature']['max']['celsius']
            min = hacks_json['forecasts'][1]['temperature']['min']['celsius']

            tomorrow = datetime.date.today()

            str = hacks_json['forecasts'][1]['date']
            tomorrow = datetime.datetime.strptime(str, "%Y-%m-%d")#""%a %d %b %Y %H:%M:%S")
            
            maxgraph[0] = int(time.mktime(tomorrow.timetuple())*1000)
            maxgraph[1] = int(max)
            mingraph[0] =  int(time.mktime(tomorrow.timetuple())*1000)
            mingraph[1] = int(min)

            tomorrowhigh.append(maxgraph)
            tomorrowlow.append(mingraph)
        except:
            max = 0.0
            min = 0.0
        logging.info('max = %s min = %s' % (max, min))

        # celsiusタグの要素をすべて取得
        maxgraph=[0, 0.0]
        mingraph=[0, 0.0]

        try:
              # 今日の予報
            max = hacks_json['forecasts'][0]['temperature']['max']['celsius']
            min = hacks_json['forecasts'][0]['temperature']['min']['celsius']

            todaY = datetime.date.today()
              # 0時を境に例外が発生するかも
            str = hacks_json['forecasts'][0]['date']
            todaY = datetime.datetime.strptime(str, "%Y-%m-%d")#""%a %d %b %Y %H:%M:%S")
            
            maxgraph[0] = int(time.mktime(todaY.timetuple())*1000)
            maxgraph[1] = int(max)
            mingraph[0] =  int(time.mktime(todaY.timetuple())*1000)
            mingraph[1] = int(min)

            todayhigh.append(maxgraph)
            todaylow.append(mingraph)
        except:
            max = 0.0
            min = 0.0
        logging.info('max = %s min = %s' % (max, min))


        #locale.setlocale(locale.LC_ALL, 'ja') 
        d = datetime.datetime.today() + datetime.timedelta(hours=8)
        kisyou_temp = 'http://www.jma.go.jp/jp/amedas/imgs/temp/206/'
        temp_filename = d.strftime("%Y%m%d%H")
        temp_url = kisyou_temp + temp_filename + '00-00.png'
        logging.info(temp_url);
        kisyou_wind = 'http://www.jma.go.jp/jp/amedas/imgs/wind/206/'
        wind_filename = d.strftime("%Y%m%d%H")
        wind_url = kisyou_wind + wind_filename + '00-00.png'
        logging.info(wind_url);
        logging.info(d.strftime("%Y%m%d%H:%M"))
         # レーダー画像は頻繁に更新されるのでhours=9で
        d = datetime.datetime.today() + datetime.timedelta(hours=9)
        kisyou_rader = 'http://www.jma.go.jp/jp/radnowc/imgs/radar/206/'
        wind_filename = d.strftime("%Y%m%d%H")
        minute = '%02d' % ((int)(d.minute/5)*5) # 五分間隔
        logging.info(minute)
        logging.info(type(minute))
        rader_url = kisyou_rader + wind_filename + minute + '-00.png'
        logging.info(rader_url);

        title = "test"
        comment = "test01"


        html = urllib2.urlopen('http://weathernews.jp/s/forecast/getcomment.cgi?&areacode=KANAGAWA&type=day').read()
        # html =  f.read()

        json_data = simplejson.loads(html)

        title =  json_data['title']
        comment =  json_data['comment']
        template_values = {
            'temp_url': temp_url,
            'wind_url': wind_url,
            'rader_url': rader_url,
            'title': title,
            'comment': comment
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def todayGraph():
        y= 0

class Guestbook(webapp.RequestHandler):
    def get(self):
        global highgraph,lowgraph
        l =[]
        l.append(highgraph)
        l.append(lowgraph)
        l.append(todayhigh)
        l.append(todaylow)
        l.append(tomorrowhigh)
        l.append(tomorrowlow)

        contstr = str(l)
        logging.info('post')
        dst = contstr.replace('L', '')
        self.response.out.write(dst)


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/getjson', Guestbook)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
