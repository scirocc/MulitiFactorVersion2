# coding=utf-8
import os,datetime
import cx_Oracle as cx
import MultiprocessFrame.main as myFrame
import pickle
import Tool.dictTrans as tool


def gen_sCode(beginT,endT):
    conn = cx.connect('market/1@192.168.0.8:1521/orcl')
    cursor=conn.cursor()
    sqlstring='select code from sh_day where(code like \'6%\')and(code<688000)and(mdate>=\'{}\')and(mdate<=\'{}\')group by code'.format(beginT,endT)
    cursor.execute('{}'.format(sqlstring))
    data=cursor.fetchall()
    temp1=[x[0] for x in data]
    sqlstring='select code from sz_day where((code like \'00%\')or(code like \'300%\'))and(mdate>=\'{}\')and(mdate<=\'{}\')group by code'.format(beginT,endT)
    cursor.execute('{}'.format(sqlstring))
    data=cursor.fetchall()
    temp2=[x[0] for x in data]
    sCode=temp1+temp2
    conn.close()
    with open('../Data/sCode','wb')as f:pickle.dump(sCode,f)
    return(sCode)

def getStockDayLineFromDb(sub_sCode,startdate,endDate):
    def dealData(data):
        if data:
            mdate, openprice, highprice, lowprice, closeprice, volume, amount, reweightfactor=data
            averPrice=amount/volume
            try:
                rehabilitationClosePrice=closeprice*reweightfactor
                rehabilitationAverPrice=averPrice*reweightfactor
            except:
                rehabilitationClosePrice = closeprice
                rehabilitationAverPrice = averPrice
            return(mdate,[round(closeprice,2),
                          round(averPrice,2),
                          round(volume,2),
                          round(amount,2),
                          round(rehabilitationClosePrice,2),
                          round(rehabilitationAverPrice,2)])

    conn = cx.connect('market/1@192.168.0.8:1521/orcl')
    cursor = conn.cursor()
    hCodeDateInfo={}
    hCodeInitInfo={}
    for code in sub_sCode:
        if code[0]=='6':tablename='sh_day'
        else:tablename='sz_day'
        sql='select mdate,openprice,highprice,lowprice,closeprice,volume,amount,reweightfactor' \
            ' from {} where(code=\'{}\')and(mdate<=\'{}\')order by mdate desc'\
                    .format(tablename,code,startdate)
        cursor.execute(sql)
        mdate,openprice,highprice,lowprice,closeprice,volume,amount,reweightfactor=cursor.fetchone()

        hCodeInitInfo[code]=[closeprice,amount/volume,volume,amount,closeprice*reweightfactor,amount/volume*reweightfactor]
        sqlstring = 'select mdate,openprice,highprice,lowprice,closeprice,volume,amount,reweightfactor' \
                    ' from {} where(code=\'{}\')and(mdate>=\'{}\')and(mdate<=\'{}\')order by mdate'\
                    .format(tablename,code,startdate,endDate)
        cursor.execute(sqlstring)
        data=cursor.fetchall()
        hDateInfo=dict(map(dealData,data))
        hCodeDateInfo[code]=hDateInfo
    with open('../Data/hCodeInitInfo','wb')as f:pickle.dump(hCodeInitInfo,f)
    conn.close()
    return (hCodeDateInfo)


def genFile(hCodeDateInfo):
    with open('../Data/hCodeInitInfo','rb')as f:hCodeInitInfo=pickle.load(f)
    #把hCodeDateInfo的停牌日的price补上
    with open('../Data/hCodeInitDate','rb')as f:hCodeInitDate=pickle.load(f)
    with open('../Data/hCodeDelistingDate','rb')as f:hCodeDelistingDate=pickle.load(f)
    h={}
    sDate=sorted(set([date for hDateinfo in hCodeDateInfo.values() for date in hDateinfo]))
    for code,hDateInfo in hCodeDateInfo.items():
        h[code]={}
        initT=hCodeInitDate[code]
        delistT=hCodeDelistingDate[code]
        sDate4code=list(filter(lambda date:initT<=date<=delistT,sDate))
        for i in range(sDate4code):
            date=sDate4code[i]
            if i==0:
                price=hCodeInitPrice[code]
                oldPrice = price
            else:
                try:#第一天保证有值
                    price=hCodeInitPrice[code]
                    oldPrice =price
                except:#没值时取上一个日子的值
                    price=oldPrice
            h[code][date]=price
    hDateCodeInfo=tool.NestDictTransfer(h)
    sDate=sorted(hDateCodeInfo)
    def dealdata(date):
        hCodeInfo=hDateCodeInfo[date]
        with open('../Data/dayline/hCodeInfoOf{}'.format(date),'wb')as f:pickle.dump(hCodeInfo,f)
        return 0
    list(map(dealdata,sDate))
    with open('../Data/sDate','wb')as f:pickle.dump(sDate,f)
    return 0

def mp_stuff(sSubsCode,sPara,hResultOfshareMemo):
    startdate, endDate=sPara
    hCodeDateInfo=getStockDayLineFromDb(sSubsCode, startdate, endDate)
    hResultOfshareMemo.update(hCodeDateInfo)
    return 0

def main(startdate,endDate):
    try:os.makedirs('../Data/dayline/')
    except:pass
    #main 只能由其他文件导入并限制在if name==main条件下
    now1=datetime.datetime.now()
    sCode=gen_sCode(startdate,endDate)
    now2=datetime.datetime.now()
    print('下载数据花费时间为：',now2-now1)
    sPara=[startdate,endDate]
    hResult=myFrame.main(sCode,mp_stuff,sPara,8)
    genFile(hResult)
    now3 = datetime.datetime.now()
    print('整理股票数据花费时间为：',now3-now2)
    return 0
#
if __name__=='__main__':
    main(20090601,20190601)

