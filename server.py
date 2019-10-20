# -*- coding: utf-8 -*-import json
from __future__ import with_statement  
from contextlib import closing  
import sqlite3  
import time  
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash  

#import psutil
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
from socket import *
import threading
import flask_excel as excel

import binascii
import Queue
import datetime
import pytz

# importsms
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

q = Queue.Queue()

global Middict
global Evpdict
global dicPara
global dicE
global historyE
dicE={}
dicPara={}
Middict={}
Evpdict={}

buffsize=1024
conn_list = []
conn_dt = {}

#Cmd645 = [0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x33,0x33,0xad,0x16]
Cmd64597 = [[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x01,0x02,0x43,0xc3,0xd5,0x16]]
Cmd645td1 = [[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x33,0x33,0xad,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x08,0x33,0x33,0x34,0x82,0xc0,0x32,0x33,0x33,0x59,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x34,0x34,0x35,0xb1,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x34,0x35,0x35,0xb2,0x16]]

Cmd645td2 = [[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x33,0x33,0xad,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x08,0x33,0x33,0x34,0x82,0xc0,0x32,0x33,0x33,0x59,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x34,0x35,0xaf,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x35,0x35,0xb0,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x36,0x35,0xb1,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x39,0x35,0xb4,0x16]]

Cmd645td = [[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x34,0x35,0xaf,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x35,0x35,0xb0,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x36,0x35,0xb1,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x32,0x39,0x35,0xb4,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x34,0x33,0xae,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x35,0x33,0xaf,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x36,0x33,0xb0,0x16],\
[0xfe,0xfe,0x68,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0x68,0x11,0x04,0x33,0x33,0x37,0x33,0xb1,0x16]]
# configsms
appid = 1234567890
appkey = "b5b822d00e899e06166faf2e624a1111"
template_id = 315404
sms_sign = "深圳市友先达电子有限公司"
params = []
ssender = SmsSingleSender(appid, appkey)

# configuration  
DATABASE = 'C:\Program Files\OpenSSH\home\cbapp\cb.db'  
DEBUG = True  
SECRET_KEY = 'development key'  
USERNAME = '1'  
PASSWORD = '1'  
async_mode = None
app = Flask(__name__)  
app.config.from_object(__name__)  
app.config.from_envvar('FLASKR_SETTINGS', silent=True)  
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

def connect_db():  
    return sqlite3.connect(app.config['DATABASE'])  
  
def init_db():  
    with closing(connect_db()) as db:  
        with app.open_resource('schema.sql') as f:  
            db.cursor().executescript(f.read())  
        db.commit()  
 
@app.before_request  
def before_request():  
    g.db = connect_db()  
 
@app.after_request  
def after_request(response):  
    g.db.close()  
    return response  

@app.route('/showE')  
def show_E(): 
    ts1=request.args.get('time1')
    ts2=request.args.get('time2')
    print(ts1)
    print(ts2)
    if ts1 and ts2:
        ts1 = datetime.datetime.strptime(ts1+' 00:00:00', "%Y/%m/%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
        ts2 = datetime.datetime.strptime(ts2+' 00:00:00', "%Y/%m/%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
    else:
        ts1 = datetime.datetime.fromtimestamp(int(time.time()) - (int(time.time())%(3600*24))-3600*8, pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        ts2 = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    print(ts1)
    print(ts2)
    global historyE
    cur = g.db.execute('select id, Biaohao, pE, nE, pQ, nQ, cishu, zongyong, shengyu, yongdian, zonggou, time_stamp from historyE where time_stamp between ? and ?',[ts1,ts2]) 
    historyE = [dict(id = row[0], Biaohao =row[1], pE=row[2], nE=row[3], pQ=row[4], nQ=row[5], cishu=row[6], zongyong=row[7], shengyu=row[8], yongdian=row[9], zonggou=row[10], time_stamp=row[11]) for row in cur.fetchall()]  
    lens=len(historyE)
    #print(historyE)
    return render_template('indexjsonE.html', historyE=historyE, len=lens)  
    
@app.route('/')  
def show_devices():  
    cur = g.db.execute('select id, Name, TaiQu, Biaohao, IP, Mid, Interval, checked, devicetype, BianBiV, BianBiI, BaoJingM, TEL from device order by id asc') 
    modbus = [dict(id = row[0], Name =row[1], TaiQu=row[2], Biaohao=row[3], IP=row[4], Mid=row[5], Interval=row[6], checked=row[7], devicetype=row[8], BianBiV=row[9], BianBiI=row[10], BaoJingM=row[11], TEL=row[12]) for row in cur.fetchall()]  
    lens=len(modbus)
    global Middict
    global dicPara
    global dicE
    global Evpdict
    if not (Middict or Evpdict) or not dicPara or not dicE:
        dicE={}
        dicPara={}
        Middict={}
        Evpdict={}
        for m in modbus:
            #print(m)
            dicE[m['Biaohao']]=[0.0,0,0.0,0.0,0.0,0.0,0,0,0.0,0.0,0.0,m['devicetype'],m['BaoJingM'],0,m['TEL']] #[6]=1需抄表 [6]=2抄表成功 [7]=1抄电量成功 [7]=2抄金额成功 [11]=devicetype [12]=BaoJingM [13]=sendedsms [14]=TEL
            dicPara[m['Biaohao']]={'U':[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              ['','','','','','','','','','','','','','','','','','','','','','','',''],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],\
              'I':[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              ['','','','','','','','','','','','','','','','','','','','','','','',''],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],\
              'P':[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              ['','','','','','','','','','','','','','','','','','','','','','','',''],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],\
              'Pf':[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
              ['','','','','','','','','','','','','','','','','','','','','','','',''],\
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]}
            if m['devicetype']==3:
                try:
                    Ipadr=m['IP']
                    Ipadrs=Ipadr.split(':')
                    print(Ipadrs)
                    if Evpdict.has_key(m['Biaohao']):
                        Evpdict[m['Biaohao']]['ip']=Ipadrs
                        Evpdict[m['Biaohao']]['Interval']=m['Interval']
                        Evpdict[m['Biaohao']]['timeout']=0.0
                        Evpdict[m['Biaohao']]['step']=0
                        Evpdict[m['Biaohao']]['status']=0
                    else:
                        Evpdict[m['Biaohao']]={}
                        Evpdict[m['Biaohao']]['ip']=Ipadrs
                        Evpdict[m['Biaohao']]['Interval']=m['Interval']
                        Evpdict[m['Biaohao']]['timeout']=0.0
                        Evpdict[m['Biaohao']]['step']=0
                        Evpdict[m['Biaohao']]['status']=0
                except Exception,err:
                    print(err) 
                
            
            if m['devicetype']==1 or m['devicetype']==2 or m['devicetype']==4 or m['devicetype']==5:
                if len(m['Mid'])==8:
                    #print(m['Mid'])
                    if Middict.has_key(m['Mid']):
                        Middict[m['Mid']]['ip']=()
                        Middict[m['Mid']]['time']=0
                        Middict[m['Mid']]['biaohao'].append(m['Biaohao'])
                        Middict[m['Mid']]['Interval'].append(m['Interval'])
                        Middict[m['Mid']]['timeout'].append(0)
                        Middict[m['Mid']]['step'].append(0)
                        Middict[m['Mid']]['status'].append(0)
                        Middict[m['Mid']]['devicetype'].append(m['devicetype'])
                    else:
                        Middict[m['Mid']]={}
                        Middict[m['Mid']]['ip']=()
                        Middict[m['Mid']]['time']=0
                        Middict[m['Mid']]['biaohao']=[]
                        Middict[m['Mid']]['biaohao'].append(m['Biaohao'])
                        Middict[m['Mid']]['Interval']=[]
                        Middict[m['Mid']]['Interval'].append(m['Interval'])
                        Middict[m['Mid']]['timeout']=[]
                        Middict[m['Mid']]['timeout'].append(0)
                        Middict[m['Mid']]['step']=[]
                        Middict[m['Mid']]['step'].append(0)
                        Middict[m['Mid']]['status']=[]
                        Middict[m['Mid']]['status'].append(0)
                        Middict[m['Mid']]['devicetype']=[]
                        Middict[m['Mid']]['devicetype'].append(m['devicetype'])
        dicE['ENDall']=0
        print(dicE)
        print(Middict)
        #print(dicPara)
        #print(Evpdict)
        print('update dic ok')
    return render_template('indexjson2.html', modbus=modbus, len=lens)  
 
@app.route('/inputdevices', methods=['POST'])  
def get_devices(): 
    if request.form.get('sub1'): 
        print('add')
        g.db.execute('insert into device (Name, TaiQu, Biaohao, IP, Mid, Interval, checked, devicetype,BianBiV,BianBiI,BaoJingM,TEL) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?)', ['', '', '', '', '', 15, 1, 1, 1, 1, 50, ''])
        g.db.commit()  
        flash('New entry was successfully add')  
    else:
        global Middict
        global dicPara
        global dicE
        global Evpdict
        dicE={}
        dicPara={}
        Middict={}
        Evpdict={}
        print('clean dic')
    return redirect(url_for('show_devices')) 
@app.route('/inputmodbus', methods=['POST'])  
def get_modbus():  
    #DeviceID= request.form['DeviceID']
    #ProductID= request.form['ProductID']
    #IP= request.form['IP']
    #PORT= request.form['PORT']
    #KEY= request.form['KEY']
    #Alivetime= request.form['Alivetime']
    
    cur = g.db.execute('select id, Name, TaiQu, Biaohao, IP, Mid, Interval, checked, devicetype from device order by id asc') 
    modbus = [dict(id = row[0], Name =row[1], TaiQu=row[2], Biaohao=row[3], IP=row[4], Mid=row[5], Interval=row[6], checked=row[7], devicetype=row[8]) for row in cur.fetchall()]  
    lens=len(modbus)
    print(lens)
    if request.form.get('sub2'):
        for m in range(lens):
            g.db.execute('UPDATE device SET Name=?,TaiQu=?,Biaohao=?,IP=?,Mid=?,Interval=?,checked=?,devicetype=?,BianBiV=?,BianBiI=?,BaoJingM=?,TEL=? where id=?', [request.form['Name%d'%(m+1)], request.form['TaiQu%d'%(m+1)], request.form['Biaohao%d'%(m+1)], request.form['IP%d'%(m+1)], request.form['Mid%d'%(m+1)], request.form['interval%d'%(m+1)], request.form['check%d'%(m+1)], request.form['devicetype%d'%(m+1)], request.form['BianBiV%d'%(m+1)], request.form['BianBiI%d'%(m+1)], request.form['BaoJingM%d'%(m+1)], request.form['TEL%d'%(m+1)], request.form['id%d'%(m+1)]])
        g.db.commit()  
        flash('New entry was successfully posted')  
    else:
        for m in range(lens):
            if request.form.get('del%d'%(m+1)):
                g.db.execute('DELETE from device where id=?', [request.form['id%d'%(m+1)]])
        g.db.commit()  
        flash('New entry was successfully deleted')  
    return redirect(url_for('show_devices'))  



def tcplink(sock,addr):
    global Middict
    global dicPara
    tmp=''
    while True:
        try:
            recvdata=sock.recv(buffsize)#.decode('utf-8')
            print(recvdata, addr)
            print(type(addr))
            try:
                response = [ord(c) for c in recvdata]
                print(response)
                if (response[0]==104) and (response[5]==104) and (response[6]==164):
                    responsemid=[0,0,0,0]
                    responsemid[0]=response[4]
                    responsemid[1]=response[3]
                    responsemid[2]=response[2]
                    responsemid[3]=response[1]
                    print(responsemid)
                    y = str(bytearray(responsemid))  
                    z = binascii.b2a_hex(y)  
                    print(z)
                    if Middict.has_key(z):
                        tmp=z
                        Middict[z]['ip']=addr
                        Middict[z]['time']=int(time.time())
                if (response[0]==104) and (response[7]==104) and (response[8]==145) and tmp:
                    for i in range(len(Middict[tmp]['biaohao'])):
                        if Middict[tmp]['step'][i]:
                            responsebh=[0,0,0,0,0,0]
                            responsebh[0]=response[6]
                            responsebh[1]=response[5]
                            responsebh[2]=response[4]
                            responsebh[3]=response[3]
                            responsebh[4]=response[2]
                            responsebh[5]=response[1]
                            print(responsebh)
                            y = str(bytearray(responsebh))
                            z = binascii.b2a_hex(y)  
                            print(z)
                            responsedata=[]
                            if Middict[tmp]['devicetype'][i]==1:
                                if z==Middict[tmp]['biaohao'][i].zfill(12) and response[10]==Cmd645td1[Middict[tmp]['step'][i]-1][12]\
                                and response[11]==Cmd645td1[Middict[tmp]['step'][i]-1][13]\
                                and response[12]==Cmd645td1[Middict[tmp]['step'][i]-1][14]\
                                and response[13]==Cmd645td1[Middict[tmp]['step'][i]-1][15]:
                                    k=response[9]
                                    for index2 in range(k-4):
                                        responsedata.append((response[14+index2]-0x33)&0xff)
                                    print(responsedata)
                                    if Middict[tmp]['step'][i]==1:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                        x=float(x)/100
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][0]=x
                                            dicE[Middict[tmp]['biaohao'][i]][7]=1
                                        
                                    elif Middict[tmp]['step'][i]==2:
                                        #ci shu
                                        x1=responsedata[4]+responsedata[5]*256
                                        print(x)
                                        #zong yong
                                        x=responsedata[6]+responsedata[7]*256+responsedata[8]*65536+responsedata[9]*16777216
                                        x2=float(x)/100
                                        print(x)
                                        #sheng yu
                                        x=responsedata[10]+responsedata[11]*256+responsedata[12]*65536+responsedata[13]*16777216
                                        x3=float(x)/100
                                        print(x)
                                        #yong dian
                                        x=responsedata[14]+responsedata[15]*256+responsedata[16]*65536+responsedata[17]*16777216
                                        x4=float(x)/100
                                        print(x)
                                        #zong gou
                                        x=responsedata[18]+responsedata[19]*256+responsedata[20]*65536+responsedata[21]*16777216
                                        x5=float(x)/100
                                        print(x)
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][1]=x1
                                            dicE[Middict[tmp]['biaohao'][i]][2]=x2
                                            dicE[Middict[tmp]['biaohao'][i]][3]=x3
                                            dicE[Middict[tmp]['biaohao'][i]][4]=x4
                                            dicE[Middict[tmp]['biaohao'][i]][5]=x5
                                            if dicE[Middict[tmp]['biaohao'][i]][7]==1:
                                                dicE[Middict[tmp]['biaohao'][i]][7]=4
                                    
                                    elif Middict[tmp]['step'][i]==3:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100
                                        x=float(x)/10
                                        if dicPara.has_key(Middict[tmp]['biaohao'][i]):
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][0].append(x)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][1].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][2].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][3].append(0)
                                            t = time.strftime('%d %H:%M', time.localtime())
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][4].append(t)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][5].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][0].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][1].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][2].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][3].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][4].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][5].pop(0)
                                            print(dicPara[Middict[tmp]['biaohao'][i]]['U'])
                                    elif Middict[tmp]['step'][i]==4:
                                        if(responsedata[2]&0x80):
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                            x=-(float(x)/1000)
                                        else:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                            x=float(x)/1000
                                        if dicPara.has_key(Middict[tmp]['biaohao'][i]):
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][0].append(x)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][1].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][2].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][3].append(0)
                                            t = time.strftime('%d %H:%M', time.localtime())
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][4].append(t)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][5].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][0].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][1].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][2].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][3].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][4].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][5].pop(0)
                                            print(dicPara[Middict[tmp]['biaohao'][i]]['I'])
                                    
                                    Middict[tmp]['status'][i]=2
                            elif Middict[tmp]['devicetype'][i]==2:
                                if z==Middict[tmp]['biaohao'][i].zfill(12) and response[10]==Cmd645td2[Middict[tmp]['step'][i]-1][12]\
                                and response[11]==Cmd645td2[Middict[tmp]['step'][i]-1][13]\
                                and response[12]==Cmd645td2[Middict[tmp]['step'][i]-1][14]\
                                and response[13]==Cmd645td2[Middict[tmp]['step'][i]-1][15]:
                                    k=response[9]
                                    for index2 in range(k-4):
                                        responsedata.append((response[14+index2]-0x33)&0xff)
                                    print(responsedata)
                                    if Middict[tmp]['step'][i]==1:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                        x=float(x)/100
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][0]=x
                                            dicE[Middict[tmp]['biaohao'][i]][7]=1
                                        
                                    elif Middict[tmp]['step'][i]==2:
                                        #ci shu
                                        x1=responsedata[4]+responsedata[5]*256
                                        print(x)
                                        #zong yong
                                        x=responsedata[6]+responsedata[7]*256+responsedata[8]*65536+responsedata[9]*16777216
                                        x2=float(x)/100
                                        print(x)
                                        #sheng yu
                                        x=responsedata[10]+responsedata[11]*256+responsedata[12]*65536+responsedata[13]*16777216
                                        x3=float(x)/100
                                        print(x)
                                        #yong dian
                                        x=responsedata[14]+responsedata[15]*256+responsedata[16]*65536+responsedata[17]*16777216
                                        x4=float(x)/100
                                        print(x)
                                        #zong gou
                                        x=responsedata[18]+responsedata[19]*256+responsedata[20]*65536+responsedata[21]*16777216
                                        x5=float(x)/100
                                        print(x)
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][1]=x1
                                            dicE[Middict[tmp]['biaohao'][i]][2]=x2
                                            dicE[Middict[tmp]['biaohao'][i]][3]=x3
                                            dicE[Middict[tmp]['biaohao'][i]][4]=x4
                                            dicE[Middict[tmp]['biaohao'][i]][5]=x5
                                            if dicE[Middict[tmp]['biaohao'][i]][7]==1:
                                                dicE[Middict[tmp]['biaohao'][i]][7]=4
                                        
                                    elif Middict[tmp]['step'][i]==3:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000
                                        x1=float(x)/1000
                                        x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100+(responsedata[6]-(responsedata[6]>>4)*6)*10000
                                        x2=float(x)/1000
                                        x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100+(responsedata[10]-(responsedata[10]>>4)*6)*10000
                                        x3=float(x)/1000
                                        if dicPara.has_key(Middict[tmp]['biaohao'][i]):
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][0].append(x1)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][1].append(x2)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][2].append(x3)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][3].append(0)
                                            t = time.strftime('%d %H:%M', time.localtime())
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][4].append(t)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][5].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][0].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][1].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][2].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][3].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][4].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['U'][5].pop(0)
                                            print(dicPara[Middict[tmp]['biaohao'][i]]['U'])
                                    
                                    elif Middict[tmp]['step'][i]==4:
                                        if(responsedata[3]&0x80):
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000
                                            x1=-(float(x)/1000)
                                        else:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000
                                            x1=float(x)/1000
                                        if(responsedata[7]&0x80):
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100+(responsedata[6]-(responsedata[6]>>4)*6)*10000
                                            x2=-(float(x)/1000)
                                        else:
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100+(responsedata[6]-(responsedata[6]>>4)*6)*10000
                                            x2=float(x)/1000
                                        if(responsedata[11]&0x80):
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100+(responsedata[10]-(responsedata[10]>>4)*6)*10000
                                            x3=-(float(x)/1000)
                                        else:
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100+(responsedata[10]-(responsedata[10]>>4)*6)*10000
                                            x3=float(x)/1000
                                        if dicPara.has_key(Middict[tmp]['biaohao'][i]):
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][0].append(x1)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][1].append(x2)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][2].append(x3)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][3].append(0)
                                            t = time.strftime('%d %H:%M', time.localtime())
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][4].append(t)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][5].append(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][0].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][1].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][2].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][3].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][4].pop(0)
                                            dicPara[Middict[tmp]['biaohao'][i]]['I'][5].pop(0)
                                            print(dicPara[Middict[tmp]['biaohao'][i]]['I'])
                                    
                                    elif Middict[tmp]['step'][i]==5:
                                        if(responsedata[3]&0x80):
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000
                                            x=-(float(x)/10000)
                                        else:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000
                                            x=float(x)/10000
                                        if(responsedata[7]&0x80):
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100+(responsedata[6]-(responsedata[6]>>4)*6)*10000
                                            x=-(float(x)/10000)
                                        else:
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100+(responsedata[6]-(responsedata[6]>>4)*6)*10000
                                            x=float(x)/10000
                                        if(responsedata[11]&0x80):
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100+(responsedata[10]-(responsedata[10]>>4)*6)*10000
                                            x=-(float(x)/10000)
                                        else:
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100+(responsedata[10]-(responsedata[10]>>4)*6)*10000
                                            x=float(x)/10000
                                        if(responsedata[15]&0x80):
                                            x=(responsedata[12]-(responsedata[12]>>4)*6)+(responsedata[13]-(responsedata[13]>>4)*6)*100+(responsedata[14]-(responsedata[14]>>4)*6)*10000
                                            x=-(float(x)/10000)
                                        else:
                                            x=(responsedata[12]-(responsedata[12]>>4)*6)+(responsedata[13]-(responsedata[13]>>4)*6)*100+(responsedata[14]-(responsedata[14]>>4)*6)*10000
                                            x=float(x)/10000
                                    
                                    elif Middict[tmp]['step'][i]==6:
                                        if(responsedata[3]&0x80):
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100
                                            x=-(float(x)/1000)
                                        else:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100
                                            x=float(x)/1000
                                        if(responsedata[7]&0x80):
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100
                                            x=-(float(x)/1000)
                                        else:
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100
                                            x=float(x)/1000
                                        if(responsedata[11]&0x80):
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100
                                            x=-(float(x)/1000)
                                        else:
                                            x=(responsedata[8]-(responsedata[8]>>4)*6)+(responsedata[9]-(responsedata[9]>>4)*6)*100
                                            x=float(x)/1000
                                        if(responsedata[15]&0x80):
                                            x=(responsedata[12]-(responsedata[12]>>4)*6)+(responsedata[13]-(responsedata[13]>>4)*6)*100
                                            x=-(float(x)/1000)
                                        else:
                                            x=(responsedata[12]-(responsedata[12]>>4)*6)+(responsedata[13]-(responsedata[13]>>4)*6)*100
                                            x=float(x)/1000
                                    
                                    Middict[tmp]['status'][i]=2
                            break
                if (response[0+3]==104) and (response[7+3]==104) and (response[8+3]==129) and tmp:
                    for i in range(len(Middict[tmp]['biaohao'])):
                        if Middict[tmp]['step'][i]:
                            responsebh=[0,0,0,0,0,0]
                            responsebh[0]=response[6+3]
                            responsebh[1]=response[5+3]
                            responsebh[2]=response[4+3]
                            responsebh[3]=response[3+3]
                            responsebh[4]=response[2+3]
                            responsebh[5]=response[1+3]
                            print(responsebh)
                            y = str(bytearray(responsebh))
                            z = binascii.b2a_hex(y)  
                            print(z)
                            responsedata=[]
                            if Middict[tmp]['devicetype'][i]==4:
                                if z==Middict[tmp]['biaohao'][i].zfill(12) and response[10+3]==Cmd64597[Middict[tmp]['step'][i]-1][12]\
                                and response[11+3]==Cmd64597[Middict[tmp]['step'][i]-1][13]:
                                    k=response[9+3]
                                    for index2 in range(k-2):
                                        responsedata.append((response[12+index2+3]-0x33)&0xff)
                                    print(responsedata)
                                    if Middict[tmp]['step'][i]==1:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                        x=float(x)/100
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][0]=x
                                            dicE[Middict[tmp]['biaohao'][i]][7]=4

                                    Middict[tmp]['status'][i]=2
                            break
                if (response[0+5]==104) and (response[7+5]==104) and (response[8+5]==129) and tmp:
                    for i in range(len(Middict[tmp]['biaohao'])):
                        if Middict[tmp]['step'][i]:
                            responsebh=[0,0,0,0,0,0]
                            responsebh[0]=response[6+5]
                            responsebh[1]=response[5+5]
                            responsebh[2]=response[4+5]
                            responsebh[3]=response[3+5]
                            responsebh[4]=response[2+5]
                            responsebh[5]=response[1+5]
                            print(responsebh)
                            y = str(bytearray(responsebh))
                            z = binascii.b2a_hex(y)  
                            print(z)
                            responsedata=[]
                            if Middict[tmp]['devicetype'][i]==5:
                                if z==Middict[tmp]['biaohao'][i].zfill(12) and response[10+5]==Cmd64597[Middict[tmp]['step'][i]-1][12]\
                                and response[11+5]==Cmd64597[Middict[tmp]['step'][i]-1][13]:
                                    k=response[9+5]
                                    for index2 in range(k-2):
                                        responsedata.append((response[12+index2+5]-0x33)&0xff)
                                    print(responsedata)
                                    if Middict[tmp]['step'][i]==1:
                                        x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                        x=float(x)/100
                                        if dicE.has_key(Middict[tmp]['biaohao'][i]):
                                            dicE[Middict[tmp]['biaohao'][i]][0]=x
                                            dicE[Middict[tmp]['biaohao'][i]][7]=4

                                    Middict[tmp]['status'][i]=2
                            break
                print(Middict)
                ts = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                print(ts)
                '''
                for tid in Middict:
                    print(tid,Middict[tid])
                    if Middict[tid]['ip']:
                        if (int(time.time()) - Middict[tid]['time'] )<600:
                            #send to all meter
                            print('send to all meter')
                        else:
                            Middict[tid]['ip']=()
                '''
            except Exception,err:
                print(err) 
            
            if not recvdata:
                print('disc')
                #sock.close()
                if tmp:
                    Middict[tmp]['ip']=()
                    print('clean ip')
                _index = conn_list.index(addr)
                conn_dt.pop(addr)
                conn_list.pop(_index)
                break
        except:
            sock.close()
            print(addr,'offline')
            if tmp:
                Middict[tmp]['ip']=()
                print('clean ip')
            _index = conn_list.index(addr)
            conn_dt.pop(addr)
            conn_list.pop(_index)
            break

def recs():
    global Middict
    global Evpdict
    global dicE
    print(Evpdict)
    print(dicE)
    print(Middict)
    s = socket(AF_INET, SOCK_STREAM)
    s.setblocking(False)
    s.bind(('0.0.0.0',8001))
    s.listen(5)
    m15 = int(time.time()) - int(time.time())%300
    m30 = int(time.time()) - int(time.time())%1800
    m60 = int(time.time()) - int(time.time())%3600
    h24 = int(time.time()) - (int(time.time())%(3600*24))
    while True:
        time.sleep(0.5)
        
        for tid in Middict:
            #print(tid,Middict[tid])
            if Middict[tid]['ip']:
                if (int(time.time()) - Middict[tid]['time'] )<600:
                    #send to all meter
                    print(tid+' send to all meter')
                else:
                    Middict[tid]['ip']=()
                    print('clean timeout ip')
        tickm15=0
        tickm30=0
        tickm60=0
        tickh24=0
        if((int(time.time())-m15)>=300):
            m15 = int(time.time()) - int(time.time())%300
            tickm15=1
            print('m15 tick')
        if((int(time.time())-m30)>=1800):
            m30 = int(time.time()) - int(time.time())%1800
            tickm30=1
            print('m30 tick')
        if((int(time.time())-m60)>=3600):
            m60 = int(time.time()) - int(time.time())%3600
            tickm60=1
            print('m60 tick')
        if((int(time.time())-h24)>=3600*24):
            h24 = int(time.time()) - (int(time.time())%(3600*24))
            tickh24=1
            print('h24 tick')
        
        for m in Evpdict:#devicetype==3 evp tick 
            if Evpdict[m]['ip']:
                try:
                    if Evpdict[m]['Interval']==15 and tickm15==1:
                        Evpdict[m]['step']=1
                        Evpdict[m]['con']=socket(AF_INET,SOCK_DGRAM)
                        Evpdict[m]['con'].setblocking(False)
                        Evpdict[m]['con'].connect((Evpdict[m]['ip'][0], int(Evpdict[m]['ip'][1])))
                        if dicE.has_key(m):
                            dicE[m][6]=1
                        Evpdict[m]['status']=0
                        print('start 15m event')
                    if Evpdict[m]['Interval']==30 and tickm30==1:
                        Evpdict[m]['step']=1
                        Evpdict[m]['con']=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        Evpdict[m]['con'].setblocking(False)
                        Evpdict[m]['con'].connect((Evpdict[m]['ip'][0], int(Evpdict[m]['ip'][1])))
                        if dicE.has_key(m):
                            dicE[m][6]=1
                        Evpdict[m]['status']=0
                        print('start 30m event')
                    if Evpdict[m]['Interval']==60 and tickm60==1:
                        Evpdict[m]['step']=1
                        Evpdict[m]['con']=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        Evpdict[m]['con'].setblocking(False)
                        Evpdict[m]['con'].connect((Evpdict[m]['ip'][0], int(Evpdict[m]['ip'][1])))
                        if dicE.has_key(m):
                            dicE[m][6]=1
                        Evpdict[m]['status']=0
                        print('start 60m event')
                    if Evpdict[m]['Interval']==1440 and tickh24==1:
                        Evpdict[m]['step']=1
                        Evpdict[m]['con']=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        Evpdict[m]['con'].setblocking(False)
                        Evpdict[m]['con'].connect((Evpdict[m]['ip'][0], int(Evpdict[m]['ip'][1])))
                        if dicE.has_key(m):
                            dicE[m][6]=1
                        Evpdict[m]['status']=0
                        print('start 24h event')
                except Exception,err:
                    print(err)
        
        for m in Middict:#devicetype=1,2 tick
            if Middict[m]['ip']:
                for i in range(len(Middict[m]['biaohao'])):
                    try:
                        if Middict[m]['Interval'][i]==15 and tickm15==1:
                            Middict[m]['step'][i]=1
                            if dicE.has_key(Middict[m]['biaohao'][i]):
                                dicE[Middict[m]['biaohao'][i]][6]=1
                            Middict[m]['status'][i]=0
                            print('start 15m event')
                        if Middict[m]['Interval'][i]==30 and tickm30==1:
                            Middict[m]['step'][i]=1
                            if dicE.has_key(Middict[m]['biaohao'][i]):
                                dicE[Middict[m]['biaohao'][i]][6]=1
                            Middict[m]['status'][i]=0
                            print('start 30m event')
                        if Middict[m]['Interval'][i]==60 and tickm60==1:
                            Middict[m]['step'][i]=1
                            if dicE.has_key(Middict[m]['biaohao'][i]):
                                dicE[Middict[m]['biaohao'][i]][6]=1
                            Middict[m]['status'][i]=0
                            print('start 60m event')
                        if Middict[m]['Interval'][i]==1440 and tickh24==1:
                            Middict[m]['step'][i]=1
                            if dicE.has_key(Middict[m]['biaohao'][i]):
                                dicE[Middict[m]['biaohao'][i]][6]=1
                            Middict[m]['status'][i]=0
                            print('start 24h event')
                        
                    except Exception,err:
                        print(err)
        
        for m in Evpdict:
            if Evpdict[m]['ip']:
                try:
                    if Evpdict[m]['status']==0 and Evpdict[m]['step']>0:
                        #start send
                        print('send evp')
                        print(Cmd645td[Evpdict[m]['step']-1])
                        senddata = str(bytearray(Cmd645td[Evpdict[m]['step']-1]))  
                        Evpdict[m]['con'].send(senddata)
                        #end send
                        Evpdict[m]['status']=1
                        Evpdict[m]['timeout']=time.time()
                        break
                    if Evpdict[m]['status']==1:
                        if time.time()-Evpdict[m]['timeout']>1.0:
                            print('time out evp'+m)
                            Evpdict[m]['status']=0
                            Evpdict[m]['step'] +=1
                            if Evpdict[m]['step']>8:
                                Evpdict[m]['step']=0
                                Evpdict[m]['con'].close
                                print('udp close')
                                if dicE.has_key(m):
                                    if dicE[m][6]==1:
                                        dicE[m][6]=2
                        else:
                            try:
                                recvdata = Evpdict[m]['con'].recv(1024)
                                response = [ord(c) for c in recvdata]
                                print(response)
                                responsedata=[]
                                if (response[0]==104) and (response[7]==104) and (response[8]==145):
                                    if response[10]==Cmd645td[Evpdict[m]['step']-1][12]\
                                    and response[11]==Cmd645td[Evpdict[m]['step']-1][13]\
                                    and response[12]==Cmd645td[Evpdict[m]['step']-1][14]\
                                    and response[13]==Cmd645td[Evpdict[m]['step']-1][15]:
                                        k=response[9]
                                        for index2 in range(k-4):
                                            responsedata.append((response[14+index2]-0x33)&0xff)
                                        print(responsedata)
                                        if Evpdict[m]['step']==5:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                            x=float(x)/100
                                            if dicE.has_key(m):
                                                dicE[m][0]=x
                                                dicE[m][7]=1
                                        elif Evpdict[m]['step']==6:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                            x=float(x)/100
                                            if dicE.has_key(m):
                                                dicE[m][8]=x
                                                if dicE[m][7]==1:
                                                    dicE[m][7]=2
                                        elif Evpdict[m]['step']==7:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                            x=float(x)/100
                                            if dicE.has_key(m):
                                                dicE[m][9]=x
                                                if dicE[m][7]==2:
                                                    dicE[m][7]=3
                                        elif Evpdict[m]['step']==8:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+(responsedata[2]-(responsedata[2]>>4)*6)*10000+(responsedata[3]-(responsedata[3]>>4)*6)*1000000
                                            x=float(x)/100
                                            if dicE.has_key(m):
                                                dicE[m][10]=x
                                                if dicE[m][7]==3:
                                                    dicE[m][7]=4
                                                print(dicE[m])
                                        elif Evpdict[m]['step']==1:
                                            x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100
                                            x1=float(x)/10
                                            x=(responsedata[2]-(responsedata[2]>>4)*6)+(responsedata[3]-(responsedata[3]>>4)*6)*100
                                            x2=float(x)/10
                                            x=(responsedata[4]-(responsedata[4]>>4)*6)+(responsedata[5]-(responsedata[5]>>4)*6)*100
                                            x3=float(x)/10
                                            if dicPara.has_key(m):
                                                dicPara[m]['U'][0].append(x1)
                                                dicPara[m]['U'][1].append(x2)
                                                dicPara[m]['U'][2].append(x3)
                                                dicPara[m]['U'][3].append(0)
                                                t = time.strftime('%d %H:%M', time.localtime())
                                                dicPara[m]['U'][4].append(t)
                                                dicPara[m]['U'][5].append(0)
                                                dicPara[m]['U'][0].pop(0)
                                                dicPara[m]['U'][1].pop(0)
                                                dicPara[m]['U'][2].pop(0)
                                                dicPara[m]['U'][3].pop(0)
                                                dicPara[m]['U'][4].pop(0)
                                                dicPara[m]['U'][5].pop(0)
                                                print(dicPara[m]['U'])
                                        
                                        elif Evpdict[m]['step']==2:
                                            if(responsedata[2]&0x80):
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                                x1=-(float(x)/1000)
                                            else:
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                                x1=float(x)/1000
                                            if(responsedata[5]&0x80):
                                                x=(responsedata[3]-(responsedata[3]>>4)*6)+(responsedata[4]-(responsedata[4]>>4)*6)*100+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*10000
                                                x2=-(float(x)/1000)
                                            else:
                                                x=(responsedata[3]-(responsedata[3]>>4)*6)+(responsedata[4]-(responsedata[4]>>4)*6)*100+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*10000
                                                x2=float(x)/1000
                                            if(responsedata[8]&0x80):
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+(responsedata[7]-(responsedata[7]>>4)*6)*100+((responsedata[8]&0x7f)-((responsedata[8]&0x7f)>>4)*6)*10000
                                                x3=-(float(x)/1000)
                                            else:
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+(responsedata[7]-(responsedata[7]>>4)*6)*100+((responsedata[8]&0x7f)-((responsedata[8]&0x7f)>>4)*6)*10000
                                                x3=float(x)/1000
                                            if dicPara.has_key(m):
                                                dicPara[m]['I'][0].append(x1)
                                                dicPara[m]['I'][1].append(x2)
                                                dicPara[m]['I'][2].append(x3)
                                                dicPara[m]['I'][3].append(0)
                                                t = time.strftime('%d %H:%M', time.localtime())
                                                dicPara[m]['I'][4].append(t)
                                                dicPara[m]['I'][5].append(0)
                                                dicPara[m]['I'][0].pop(0)
                                                dicPara[m]['I'][1].pop(0)
                                                dicPara[m]['I'][2].pop(0)
                                                dicPara[m]['I'][3].pop(0)
                                                dicPara[m]['I'][4].pop(0)
                                                dicPara[m]['I'][5].pop(0)
                                                print(dicPara[m]['I'])
                                        
                                        elif Evpdict[m]['step']==3:
                                            if(responsedata[2]&0x80):
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                                x=-(float(x)/10000)
                                            else:
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+(responsedata[1]-(responsedata[1]>>4)*6)*100+((responsedata[2]&0x7f)-((responsedata[2]&0x7f)>>4)*6)*10000
                                                x=float(x)/10000
                                            if(responsedata[5]&0x80):
                                                x=(responsedata[3]-(responsedata[3]>>4)*6)+(responsedata[4]-(responsedata[4]>>4)*6)*100+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*10000
                                                x=-(float(x)/10000)
                                            else:
                                                x=(responsedata[3]-(responsedata[3]>>4)*6)+(responsedata[4]-(responsedata[4]>>4)*6)*100+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*10000
                                                x=float(x)/10000
                                            if(responsedata[8]&0x80):
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+(responsedata[7]-(responsedata[7]>>4)*6)*100+((responsedata[8]&0x7f)-((responsedata[8]&0x7f)>>4)*6)*10000
                                                x=-(float(x)/10000)
                                            else:
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+(responsedata[7]-(responsedata[7]>>4)*6)*100+((responsedata[8]&0x7f)-((responsedata[8]&0x7f)>>4)*6)*10000
                                                x=float(x)/10000
                                            if(responsedata[11]&0x80):
                                                x=(responsedata[9]-(responsedata[9]>>4)*6)+(responsedata[10]-(responsedata[10]>>4)*6)*100+((responsedata[11]&0x7f)-((responsedata[11]&0x7f)>>4)*6)*10000
                                                x=-(float(x)/10000)
                                            else:
                                                x=(responsedata[9]-(responsedata[9]>>4)*6)+(responsedata[10]-(responsedata[10]>>4)*6)*100+((responsedata[11]&0x7f)-((responsedata[11]&0x7f)>>4)*6)*10000
                                                x=float(x)/10000
                                        
                                        elif Evpdict[m]['step']==4:
                                            if(responsedata[1]&0x80):
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+((responsedata[1]&0x7f)-((responsedata[1]&0x7f)>>4)*6)*100
                                                x=-(float(x)/1000)
                                            else:
                                                x=(responsedata[0]-(responsedata[0]>>4)*6)+((responsedata[1]&0x7f)-((responsedata[1]&0x7f)>>4)*6)*100
                                                x=float(x)/1000
                                            if(responsedata[3]&0x80):
                                                x=(responsedata[2]-(responsedata[2]>>4)*6)+((responsedata[3]&0x7f)-((responsedata[3]&0x7f)>>4)*6)*100
                                                x=-(float(x)/1000)
                                            else:
                                                x=(responsedata[2]-(responsedata[2]>>4)*6)+((responsedata[3]&0x7f)-((responsedata[3]&0x7f)>>4)*6)*100
                                                x=float(x)/1000
                                            if(responsedata[5]&0x80):
                                                x=(responsedata[4]-(responsedata[4]>>4)*6)+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*100
                                                x=-(float(x)/1000)
                                            else:
                                                x=(responsedata[4]-(responsedata[4]>>4)*6)+((responsedata[5]&0x7f)-((responsedata[5]&0x7f)>>4)*6)*100
                                                x=float(x)/1000
                                            if(responsedata[7]&0x80):
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+((responsedata[7]&0x7f)-((responsedata[7]&0x7f)>>4)*6)*100
                                                x=-(float(x)/1000)
                                            else:
                                                x=(responsedata[6]-(responsedata[6]>>4)*6)+((responsedata[7]&0x7f)-((responsedata[7]&0x7f)>>4)*6)*100
                                                x=float(x)/1000
                                        
                                        Evpdict[m]['status']=2
                                    
                                
                            except Exception,err:
                                print(err)
                        break
                    if Evpdict[m]['status']==2:
                        print('rx ok evp'+m)
                        Evpdict[m]['status']=0
                        Evpdict[m]['step'] +=1
                        if Evpdict[m]['step']>8:
                            Evpdict[m]['step']=0
                            Evpdict[m]['con'].close
                            print('udp close')
                            if dicE.has_key(m):
                                if dicE[m][6]==1:
                                    dicE[m][6]=2
                        break
                except Exception,err:
                    print(err)
        
        for m in Middict:
            if Middict[m]['ip']:
                for i in range(len(Middict[m]['biaohao'])):
                    try:
                        if Middict[m]['status'][i]==0 and Middict[m]['step'][i]>0:
                            #start send
                            con = conn_dt[Middict[m]['ip']]
                            #senddata = str(bytearray(Cmd645))  
                            #con.send(senddata)
                            print(Middict[m]['biaohao'][i])
                            if Middict[m]['biaohao'][i]:
                                y=bytearray.fromhex(Middict[m]['biaohao'][i].zfill(12))
                                Maddr = list(y)
                            else:
                                y=bytearray.fromhex('111111111111')
                                Maddr = list(y)
                            print(Maddr)
                            BH=[0,0,0,0,0,0]
                            #if len(Maddr)>=6:
                            for index in range(6):
                                BH[index]=Maddr[6-1-index]
                            #else:
                            #    for index in range(len(Maddr)):
                            #        BH[index]=Maddr[len(Maddr)-1-index]
                            #    for index in range(6-len(Maddr)):
                            #        BH[len(Maddr)+index]=0
                            
                            if Middict[m]['devicetype'][i]==1:
                                for index in range(6):
                                    Cmd645td1[Middict[m]['step'][i]-1][index+3]=BH[index]
                                lensdata=len(Cmd645td1[Middict[m]['step'][i]-1])
                                Cmd645td1[Middict[m]['step'][i]-1][lensdata-2]=0
                                for index in range(2,lensdata-2):
                                    Cmd645td1[Middict[m]['step'][i]-1][lensdata-2] +=Cmd645td1[Middict[m]['step'][i]-1][index]
                                Cmd645td1[Middict[m]['step'][i]-1][lensdata-2] = Cmd645td1[Middict[m]['step'][i]-1][lensdata-2]&0xff;
                                print(Cmd645td1[Middict[m]['step'][i]-1])
                                senddata = str(bytearray(Cmd645td1[Middict[m]['step'][i]-1]))  
                                con.send(senddata)
                            elif Middict[m]['devicetype'][i]==2:
                                for index in range(6):
                                    Cmd645td2[Middict[m]['step'][i]-1][index+3]=BH[index]
                                lensdata=len(Cmd645td2[Middict[m]['step'][i]-1])
                                Cmd645td2[Middict[m]['step'][i]-1][lensdata-2]=0
                                for index in range(2,lensdata-2):
                                    Cmd645td2[Middict[m]['step'][i]-1][lensdata-2] +=Cmd645td2[Middict[m]['step'][i]-1][index]
                                Cmd645td2[Middict[m]['step'][i]-1][lensdata-2] = Cmd645td2[Middict[m]['step'][i]-1][lensdata-2]&0xff;
                                print(Cmd645td2[Middict[m]['step'][i]-1])
                                senddata = str(bytearray(Cmd645td2[Middict[m]['step'][i]-1]))  
                                con.send(senddata)
                            elif Middict[m]['devicetype'][i]==4:
                                for index in range(6):
                                    Cmd64597[Middict[m]['step'][i]-1][index+3]=BH[index]
                                lensdata=len(Cmd64597[Middict[m]['step'][i]-1])
                                Cmd64597[Middict[m]['step'][i]-1][lensdata-2]=0
                                for index in range(2,lensdata-2):
                                    Cmd64597[Middict[m]['step'][i]-1][lensdata-2] +=Cmd64597[Middict[m]['step'][i]-1][index]
                                Cmd64597[Middict[m]['step'][i]-1][lensdata-2] = Cmd64597[Middict[m]['step'][i]-1][lensdata-2]&0xff;
                                print(Cmd64597[Middict[m]['step'][i]-1])
                                senddata = str(bytearray(Cmd64597[Middict[m]['step'][i]-1]))  
                                con.send(senddata)
                            elif Middict[m]['devicetype'][i]==5:
                                for index in range(6):
                                    Cmd64597[Middict[m]['step'][i]-1][index+3]=BH[index]
                                lensdata=len(Cmd64597[Middict[m]['step'][i]-1])
                                Cmd64597[Middict[m]['step'][i]-1][lensdata-2]=0
                                for index in range(2,lensdata-2):
                                    Cmd64597[Middict[m]['step'][i]-1][lensdata-2] +=Cmd64597[Middict[m]['step'][i]-1][index]
                                Cmd64597[Middict[m]['step'][i]-1][lensdata-2] = Cmd64597[Middict[m]['step'][i]-1][lensdata-2]&0xff;
                                print(Cmd64597[Middict[m]['step'][i]-1])
                                senddata = str(bytearray(Cmd64597[Middict[m]['step'][i]-1]))  
                                con.send(senddata)
                            #end send
                            Middict[m]['status'][i]=1
                            Middict[m]['timeout'][i]=int(time.time())
                            break
                        if Middict[m]['status'][i]==1:
                            if int(time.time())-Middict[m]['timeout'][i]>30:
                                print('time out '+Middict[m]['biaohao'][i])
                                Middict[m]['status'][i]=0
                                Middict[m]['step'][i] +=1
                                if Middict[m]['devicetype'][i]==1:
                                    if Middict[m]['step'][i]>4:
                                        Middict[m]['step'][i]=0
                                        if dicE.has_key(Middict[m]['biaohao'][i]):
                                            if dicE[Middict[m]['biaohao'][i]][6]==1:
                                                dicE[Middict[m]['biaohao'][i]][6]=2
                                elif Middict[m]['devicetype'][i]==2:
                                    if Middict[m]['step'][i]>6:
                                        Middict[m]['step'][i]=0
                                        if dicE.has_key(Middict[m]['biaohao'][i]):
                                            if dicE[Middict[m]['biaohao'][i]][6]==1:
                                                dicE[Middict[m]['biaohao'][i]][6]=2
                                elif Middict[m]['devicetype'][i]==4:
                                    if Middict[m]['step'][i]>1:
                                        Middict[m]['step'][i]=0
                                        if dicE.has_key(Middict[m]['biaohao'][i]):
                                            if dicE[Middict[m]['biaohao'][i]][6]==1:
                                                dicE[Middict[m]['biaohao'][i]][6]=2
                                elif Middict[m]['devicetype'][i]==5:
                                    if Middict[m]['step'][i]>1:
                                        Middict[m]['step'][i]=0
                                        if dicE.has_key(Middict[m]['biaohao'][i]):
                                            if dicE[Middict[m]['biaohao'][i]][6]==1:
                                                dicE[Middict[m]['biaohao'][i]][6]=2
                            break
                        if Middict[m]['status'][i]==2:
                            print('rx ok '+Middict[m]['biaohao'][i])
                            Middict[m]['status'][i]=0
                            Middict[m]['step'][i] +=1
                            if Middict[m]['devicetype'][i]==1:
                                if Middict[m]['step'][i]>4:
                                    Middict[m]['step'][i]=0
                                    if dicE.has_key(Middict[m]['biaohao'][i]):
                                        if dicE[Middict[m]['biaohao'][i]][6]==1:
                                            dicE[Middict[m]['biaohao'][i]][6]=2
                            elif Middict[m]['devicetype'][i]==2:
                                if Middict[m]['step'][i]>6:
                                    Middict[m]['step'][i]=0
                                    if dicE.has_key(Middict[m]['biaohao'][i]):
                                        if dicE[Middict[m]['biaohao'][i]][6]==1:
                                            dicE[Middict[m]['biaohao'][i]][6]=2
                            elif Middict[m]['devicetype'][i]==4:
                                if Middict[m]['step'][i]>1:
                                    Middict[m]['step'][i]=0
                                    if dicE.has_key(Middict[m]['biaohao'][i]):
                                        if dicE[Middict[m]['biaohao'][i]][6]==1:
                                            dicE[Middict[m]['biaohao'][i]][6]=2
                            elif Middict[m]['devicetype'][i]==5:
                                if Middict[m]['step'][i]>1:
                                    Middict[m]['step'][i]=0
                                    if dicE.has_key(Middict[m]['biaohao'][i]):
                                        if dicE[Middict[m]['biaohao'][i]][6]==1:
                                            dicE[Middict[m]['biaohao'][i]][6]=2
                            break
                    except Exception,err:
                        print(err)
        
        counter1=0
        counter2=0
        try:
            for m in dicE:
                if m != 'ENDall':
                    if dicE[m][6]>0:
                        counter1 +=1
                    if counter1>0:
                        if dicE[m][6]==2:
                            counter2 +=1
            if counter1==counter2 and counter1:
                dicE['ENDall']=1
            if dicE['ENDall']==1:
                try:
                    cx = sqlite3.connect(DATABASE)
                    for m in dicE:
                        if m != 'ENDall':
                            if dicE[m][6]==2 and dicE[m][7]==4:
                                cx.execute('insert into historyE (Biaohao, pE, cishu, zongyong, shengyu, yongdian, zonggou, nE, pQ, nQ)\
                                  values (?, ?, ?, ?, ?, ?, ?, ?, ? ,?)', [m,dicE[m][0], dicE[m][1], dicE[m][2], \
                                  dicE[m][3], dicE[m][4], dicE[m][5], dicE[m][8], dicE[m][9], dicE[m][10]])
                                if (dicE[m][11]==1 or dicE[m][11]==2) and dicE[m][14]:# get BaoJingM and TEL
                                    if dicE[m][3]<dicE[m][12]:
                                        if dicE[m][13]==0:
                                            try:
                                                params=[]
                                                strfloat='%.2f'%dicE[m][3]
                                                params.append(strfloat)
                                                result = ssender.send_with_param(86, dicE[m][14],\
                                                  template_id, params, sign=sms_sign, extend="", ext="")  # 签名参数未提供或者为空时，会使用默认签名发送短信
                                                dicE[m][13]=1
                                            except HTTPError as e:
                                                print(e)
                                            except Exception as e:
                                                print(e)
                                            print(result)
                                    else:
                                        dicE[m][13]=0
                                    
                            dicE[m][6]=0
                            dicE[m][7]=0
                    cx.commit() 
                except Exception,err:
                    print(err)
                print('cb end')
                print(dicE)
                dicE['ENDall']=0
        except Exception,err:
            print(err)
        try:
            clientsock,clientaddress=s.accept()
        except Exception,err:
            print(err)
            continue
        clientsock.setblocking(True)
        if clientaddress not in conn_list:
            conn_list.append(clientaddress)
        conn_dt[clientaddress] = clientsock
        print('connect from:',clientaddress)
        #在这里创建线程，就可以每次都将socket进行保持
        t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))
        t.start()
        print(conn_dt)
        print(conn_list)

# 后台线程 产生数据，即刻推送至前端
def background_thread():
    """Example of how to send server generated events to clients."""

    t1 = threading.Thread(target=recs, args=(), name='rec')
    t1.start()
    global dicPara
    count = 0
    tu=()
    while True:
        socketio.sleep(5)
        try:
            while not q.empty():
                tu=q.get()
                count = 0
                if dicPara.has_key(tu[0]):
                    if dicPara[tu[0]].has_key(tu[1]):
                        for i in range(len(dicPara[tu[0]][tu[1]][0])):
                            count += 1
                            socketio.emit('server_response',\
                              {'data': [dicPara[tu[0]][tu[1]][4][i], dicPara[tu[0]][tu[1]][0][i],dicPara[tu[0]][tu[1]][1][i],dicPara[tu[0]][tu[1]][2][i],dicPara[tu[0]][tu[1]][3][i]], 'count': count},\
                              namespace='/test')
                            dicPara[tu[0]][tu[1]][5][i]=1
                            #print(dicPara[tu[0]])
                            
                        
            #count += 1
            #t = time.strftime('%H:%M:%S', time.localtime()) # 获取系统时间（只取分:秒）
            #cpus = psutil.cpu_percent(interval=None, percpu=True) # 获取系统cpu使用率 non-blocking
            if tu:
                if not dicPara[tu[0]][tu[1]][5][23]: 
                    count += 1
                    socketio.emit('server_response',\
                          {'data': [dicPara[tu[0]][tu[1]][4][23], dicPara[tu[0]][tu[1]][0][23],dicPara[tu[0]][tu[1]][1][23],dicPara[tu[0]][tu[1]][2][23],dicPara[tu[0]][tu[1]][3][23]], 'count': count},\
                          namespace='/test') # 注意：这里不需要客户端连接的上下文，默认 broadcast = True ！！！！！！！
                    dicPara[tu[0]][tu[1]][5][23]=1
                    #print(dicPara[tu[0]])
        except Exception,err:
            print(err)
        
@app.route('/index', methods=['get'])
def index():
    id=request.args.get('id')
    cur = g.db.execute('select id, Name, TaiQu, Biaohao, IP, Mid, Interval, checked, devicetype from device order by id asc') 
    modbus = [dict(id = row[0], Name =row[1], TaiQu=row[2], Biaohao=row[3], IP=row[4], Mid=row[5], Interval=row[6], checked=row[7], devicetype=row[8]) for row in cur.fetchall()]  
    lens=len(modbus)
    print(type(id))
    for m in modbus:
        print(m['id'])
        if id:
            if m['id']==int(id):
                print((m['Biaohao'],'U'))
                q.put((m['Biaohao'],'U'))
    return render_template('index.html', async_mode=socketio.async_mode, modbus=modbus, len=lens)  
    #return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/indexI', methods=['get'])
def index_I():
    id=request.args.get('id')
    cur = g.db.execute('select id, Name, TaiQu, Biaohao, IP, Mid, Interval, checked, devicetype from device order by id asc') 
    modbus = [dict(id = row[0], Name =row[1], TaiQu=row[2], Biaohao=row[3], IP=row[4], Mid=row[5], Interval=row[6], checked=row[7], devicetype=row[8]) for row in cur.fetchall()]  
    lens=len(modbus)
    print(type(id))
    for m in modbus:
        print(m['id'])
        if id:
            if m['id']==int(id):
                print((m['Biaohao'],'I'))
                q.put((m['Biaohao'],'I'))
    return render_template('indexI.html', async_mode=socketio.async_mode, modbus=modbus, len=lens)  
    #return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/search", methods=['GET','POST'])
def download_file():
    time1=''
    time2=''
    if request.form.get('sub1'):
        time1=request.form['time1']
        time2=request.form['time2']
        print(request.form['time1'])
        print(request.form['time2'])
    if request.form.get('sub2'):
        #cur = g.db.execute('select id, Biaohao, pE, nE, pQ, nQ, cishu, zongyong, shengyu, yongdian, zonggou, time_stamp from historyE') 
        #historyE = [[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]] for row in cur.fetchall()]  
        global historyE
        if historyE:
            historyEE = [[row['id'], row['Biaohao'], row['pE'], row['nE'], row['pQ'], row['nQ'], row['cishu'], row['zongyong'], row['shengyu'], row['yongdian'], row['zonggou'], row['time_stamp']] for row in historyE]  
            historyEE.insert(0,['id','Biaohao','pE','nE','pQ','nQ','cishu','zongyong','shengyu','yongdian','zonggou','time_stamp'])
            return excel.make_response_from_array(historyEE, "csv", file_name='down.csv')
    return redirect(url_for('show_E',time1=time1,time2=time2)) 
# 与前端建立 socket 连接后，启动后台线程
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    excel.init_excel(app)
    socketio.run(app, debug=True, host='0.0.0.0',port=8081)
    
