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
    return(sCode)

def getStockDayLineFromDb(sub_sCode,startdate,endDate):
    def dealData(data):
        if data:
            mdate, openprice, highprice, lowprice, closeprice, volume, amount, reweightfactor=data
            averPrice=amount/volume
            rehabilitationClosePrice=closeprice*reweightfactor
            rehabilitationAverPrice=averPrice*reweightfactor
            return(mdate,[closeprice,averPrice,volume,amount,rehabilitationClosePrice,rehabilitationAverPrice])

    conn = cx.connect('market/1@192.168.0.8:1521/orcl')
    cursor = conn.cursor()
    hCodeDateInfo={}
    for code in sub_sCode:
        if code[0]=='6':tablename='sh_day'
        else:tablename='sz_day'
        sqlstring = 'select mdate,openprice,highprice,lowprice,closeprice,volume,amount,reweightfactor' \
                    ' from {} where(code=\'{}\')and(mdate>=\'{}\')and(mdate<=\'{}\')order by mdate'\
                    .format(tablename,code,startdate,endDate)
        cursor.execute(sqlstring)
        data=cursor.fetchall()
        hDateInfo=dict(map(dealData,data))
        hCodeDateInfo[code]=hDateInfo
    conn.close()
    return (hCodeDateInfo)


def genFile(hCodeDateInfo):
    hDateCodeInfo=tool.NestDictTransfer(hCodeDateInfo)
    sDate=sorted(hDateCodeInfo)
    def dealdata(date):
        hCodeInfo=hDateCodeInfo(date)
        with open('../data/dayline/hCodeInfoOf{}'.format(date),'w')as f:pickle.dump(hCodeInfo,f)
        return 0
    list(map(dealdata,sDate))
    with open('../data/sDate','w')as f:pickle.dump(sDate,f)
    return 0

def mp_stuff(sSubsCode,sPara,hResultOfshareMemo):
    startdate, endDate=sPara
    hCodeDateInfo=getStockDayLineFromDb(sSubsCode, startdate, endDate)
    hResultOfshareMemo.update(hCodeDateInfo)
    return 0

def main(startdate,endDate):
    try:os.makedirs('../data/dayline/')
    except:pass
    #main 只能由其他文件导入并限制在if name==main条件下
    now1=datetime.datetime.now()
    sCode=gen_sCode(startdate,endDate)
    now2=datetime.datetime.now()
    print('下载数据花费时间为：',now2-now1)
    sPara=[startdate,endDate]
    hResultOfshareMemo=myFrame.main(sCode,mp_stuff,sPara)
    genFile(hResultOfshareMemo)
    now3 = datetime.datetime.now()
    print('整理股票数据花费时间为：',now3-now2)
    return 0
#
# if __name__=='__main__':
#     main(20090601,20190601)
