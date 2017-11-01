# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time
import pymysql

time_flag = True
conn = pymysql.connect(host='bitcoinratedb.c2cepwfsnb3t.ap-northeast-1.rds.amazonaws.com'
                       ,port=3306,user='yamashirotakurou',passwd='Yamataku2280Kt',db='mysql',charset='utf8')
cur = conn.cursor()
cur.execute("USE menagerie")
cur.close()
conn.close()


while True:
    f = open("bitcoin_rate.csv","a")
    writer = csv.writer(f, lineterminator='\n')
    csv_list = []
    time_is = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    # アクセスするURL
    url = "https://cc.minkabu.jp/pair/BTC_JPY"

    # URLにアクセスする htmlが帰ってくる → <html><head><title>hogehoge</title></head><body....
    http = urllib3.PoolManager()
    
    html = http.request('GET', url)

    # htmlをBeautifulSoupで扱う
    soup = BeautifulSoup(html.data, "html5lib")

    # span要素全てを摘出する→全てのspan要素が配列に入ってかえされます→[<span class="m-wficon triDown"></span>, <span class="l-h...
    span = soup.find_all("span")

    # print時のエラーとならないように最初に宣言しておきます。
    bitcoin_rate = ""
    # for分で全てのspan要素の中からid="btc_jpn_top_bid"となっている物を探します
    for tag in span:
        # classの設定がされていない要素は、tag.get("id")を行うことのできないでエラーとなるため、tryでエラーを回避する
        try:
            # tagの中からclass="n"のnの文字列を摘出します。複数classが設定されている場合があるので
            # get関数では配列で帰ってくる。そのため配列の関数pop(0)により、配列の一番最初を摘出する
            # <span class="hoge" class="foo">  →   ["hoge","foo"]  →   hoge
            string_ = tag.get("id")
            # 摘出したclassの文字列にbtc_jpy_top_bidと設定されているかを調べます
            if string_ in "btc_jpy_top_bid":
                # btc_jpy_top_bidが設定されているのでtagで囲まれた文字列を.stringであぶり出します
                bitcoin_rate = tag.string
                # 摘出が完了したのでfor分を抜けます
                break
        except:
            # パス→何も処理を行わない
            pass
    # 摘出した1ビットコインの価格を時間とともに出力します。
    bitcoin_rate = bitcoin_rate.strip()
    bitcoin_rate = bitcoin_rate.replace(",","")
    print (time_is + ' , '+ '¥' + bitcoin_rate)
    # 1カラム目に時刻を記録します
    #csv_list.append(time_is)
    # 2カラム目に1ビットコインの価格を記録します
    #csv_list.append(bitcoin_rate)
    # csvに追記敷きます
    writer.writerow(csv_list)
    # ファイル破損防止のために閉じます
    f.close()
    #１分間待ちます
    time.sleep(60)

