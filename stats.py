#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#==============================================================================
# 市場の流れを掴む変数を出す
# レートが大きく揺れ動いた時にメールを送信して通知する
#==============================================================================


"""
Created on Sun Oct 22 18:25:18 2017

@author: yamashirotakurou
"""

import pymysql
import time
import numpy as np
import math
import setup
import setup_mail
import smtplib
from email.mime.text import MIMEText

#価格が一定以上変動した場合のフラグ
sigmaflag = 0
mailflag = 0

while True:

    #コネクタ
    conn = pymysql.connect(host=setup.host,
                           port=3306,
                           user='yamashirotakurou',
                           passwd=setup.pw,
                           db='mysql',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    
    #カーソルを設定
    cur = conn.cursor()
    
    #使うデータベースを指定
    cur.execute("USE bitcoin_rate")
    
    #テーブルの行数を数える(外れ値は除去する)
    cur.execute("SELECT count(*) FROM trade WHERE id >= 150 AND rate > 100000")
    
    #正常値の数を入力し変数に代入
    count = cur.fetchone()['count(*)']
    
    #異常値の数を変数に代入
    cur.execute("SELECT count(*) FROM trade WHERE id >= 150 AND rate < 100000")
    count_err = cur.fetchone()['count(*)']
    
    #異常値を除いた1440項目前の値のid
    count_yest = count-59-count_err
    
    #ビットコインのレート情報を入力(外れ値は同じく除去する)
    cur.execute("SELECT rate FROM trade WHERE id >= %s AND rate > 100000",(count_yest))
    rates = cur.fetchall()
    
    #データを配列にする
    rate_list = []
    for rate in rates:
        rate_list.append(rate['rate'])
        
    #現在の価格を取得する
    cur.execute("SELECT rate FROM trade WHERE id = %s",(149+count+count_err))
    rate_now = cur.fetchone()['rate']
    
    #平均を取る
    rate_ave = np.average(rate_list)
    sigma = np.std(rate_list)
    
    #小数点以下を切り捨てる
    rate_ave = math.floor(rate_ave)
        
    print("now rate is "+str(rate_now) )
    print("today's average : "+str(rate_ave) )
    print("today's sigma : "+str(sigma) )
    if rate_ave - sigma > rate_now:
        print("CHANCE!!!")
        sigmaflag = 1
    else :
        sigmaflag = 0
        mailflag = 0
    #レートが-1シグマを割ったらメールで通知を送る
    if sigmaflag == 1 and mailflag == 0:
#        msg = MIMEText("now rate is "+str(rate_now))
#        msg['Subject'] = "価格下落"
#        msg['From'] = "yt1997kt@icloud.com"
#        msg['To'] = "yt1997kt@gmail.com"
#        #下記のパラメータは https://support.apple.com/ja-jp/HT202304 によった
#        s = smtplib.SMTP('smtp.mail.me.com',587)
#        s.ehlo()
#        s.starttls()
#        s.login(setup_mail.name,setup_mail.pw)
#        s.send_message(msg)
#        s.quit()
        #何度も連続でメールが送られることがないようにフラグを立てる
        mailflag = 1
        
    
    cur.close()
    conn.close()
    
    time.sleep(55)

