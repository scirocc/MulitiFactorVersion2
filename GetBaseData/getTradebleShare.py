# coding=utf-8
import requests,time,pickle,glob
import threading as td
import queue


def get_sCode():
    sFile=glob.glob('E:\pyProjectData\MultiFactor\Data\stockDayLine/*.csv')
    sCode=[x[-10:-4] for x in sFile]
    return(sCode)

def divide_to_subsCode(sCode,num_of_mp):
    whole_nums=len(sCode)
    sSUBsCode=[sCode[slice(i,whole_nums,num_of_mp)] for i in range(num_of_mp)]
    return(sSUBsCode)

def td_do(sCode,q,endT):
    url='https://fyal7tbfnf.execute-api.cn-north-1.amazonaws.com.cn/ALPHA/openapi/htsc-fic-cdsinter-open/IInterProvider/getResourceData'
    headers = {'Content-Type': 'application/json','authorization': 'b932a6ec0f3bef993326983f5c8808eb'}
    for code in sCode:
        # ibay-15810255059
        markOfError=True
        while markOfError:
            try:
                data={#查询所属行业
                    "resource": "ZX_COMPANYINDUSTRY",
                    'key': '769c94a5bc5f4e349ded788469940f38',
                    "paramMaps": {
                        "TRADINGCODE": ["{}".format(code)],
                    },
                    "startrow":0,
                    "rownum":1,
                    "selectedFields":["FINDUNAME"]
                    }
                Indus=eval(requests.post(url=url,headers=headers,json=data).text)['dataList'][0]['FINDUNAME']
                # 查询上市退市日期
                data={
                    "resource": "ZX_STKBASICINFO",
                    'key': '769c94a5bc5f4e349ded788469940f38',
                    "paramMaps": {
                        "TRADINGCODE": ["{}".format(code)],
                    },
                    "startrow":0,
                    "rownum":5,
                    "selectedFields":["LISTINGDATE","DELISTINGDATE"]
                    }
                text=requests.post(url=url,headers=headers,json=data).text.replace('null','-1')
                Initialdate=(eval(text)['dataList'][0]['LISTINGDATE'])
                Initialdate=(time.strftime('%Y%m%d', time.localtime(Initialdate/1000)))
                DelistingDate=eval(text)['dataList'][0]['DELISTINGDATE']
                if DelistingDate!=-1:
                    DelistingDate=int(time.strftime('%Y%m%d', time.localtime(DelistingDate/1000)))
                #
                # 查询流通股有变化的所有信息
                data={
                    "resource": "ZX_SHARECHANGE",
                    'key': '769c94a5bc5f4e349ded788469940f38',
                     "paramMaps": {
                        "TRADINGCODE": ["{}".format(code)],
                        "ENDDATE": ["[{},{}]".format(Initialdate,endT)]
                    },
                    "startrow":0,
                    "rownum":10000,
                    "orderBy":"ENDDATE",
                    "selectedFields":[
                        "ENDDATE",
                        "ATOTALSHARE",
                        "ALISTEDSHARE",#流通A
                    ]
                }
                sData=eval((requests.post(url=url,headers=headers,json=data).text))['dataList']
                hDateTradableShares={}
                for data in sData:
                    tradableShares=data['ALISTEDSHARE']*10000
                    date=int(time.strftime('%Y%m%d', time.localtime(data['ENDDATE']/1000)))
                    hDateTradableShares[date]=tradableShares
                #
                # #查询前十流通股东
                data = {
                    "resource": "ZX_STKSHAREHOLDER", # 资源名称
                    'key': '769c94a5bc5f4e349ded788469940f38',
                    "startrow": "0", # 分页偏移
                    "rownum": "10000", # 每页条数
                    "orderBy": "ENDDATE", # 排序字段
                    "selectedFields":[
                            "ENDDATE",
                            "SHNAME",
                            "HOLDASHARE",
                            "SHNATURE"
                    ],
                    "paramMaps": {
                        "TRADINGCODE": ["{}".format(code)],
                        "SHTYPE":["20"],#只查询流通股东
                        "ENDDATE": ["[{},{})".format(Initialdate,endT)],
                    }
                }
                text=requests.post(url=url,headers=headers,json=data).text.replace('null','"null"')
                sData=eval(text)['dataList']
                hDateDetailsOfshareHolders={}
                for data in sData:
                    date=int(time.strftime('%Y%m%d', time.localtime(data['ENDDATE']/1000)))
                    num_of_shares=data['HOLDASHARE']
                    name_of_shareholder=data['SHNAME']
                    kind_of_shareholder=data['SHNATURE']
                    if date in hDateDetailsOfshareHolders.keys():
                        hDateDetailsOfshareHolders[date].append([num_of_shares,name_of_shareholder,kind_of_shareholder])
                    else:
                        hDateDetailsOfshareHolders[date]=[[num_of_shares,name_of_shareholder,kind_of_shareholder]]

                #查询实控人
                data = {
                    "resource": "ZX_ASSOCBUSINESS", # 资源名称
                    'key': '769c94a5bc5f4e349ded788469940f38',
                    "startrow": "0", # 分页偏移
                    "rownum": "1", # 每页条数
                    "orderBy": "", # 排序字段
                    "selectedFields":["ASSOCNAME"
                     ],
                    "paramMaps": {
                        "TRADINGCODE": ["{}".format(code)],
                    }
                }
                try:sActualController=eval(requests.post(url=url,headers=headers,json=data).text)['dataList'][0]['ASSOCNAME'].split(',')
                except:sActualController=[]
                #信息汇总
                Info=[Indus,hDateTradableShares,hDateDetailsOfshareHolders,sActualController,code,DelistingDate]
                q.put(Info)
                markOfError=False
                print('{} stock\'s info has done'.format(q.qsize()))
            except:
                pass
    return 0


def dealWithInfo(q):
    hCodeIndus={}
    hCodeDelistingDate={}
    hCodeDateActualTradableShare={}
    for i in range(q.qsize()):
        Indus,hDateTradableShares,hDateDetailsOfshareHolders,sActualController,code,DelistingDate=q.get()
        if DelistingDate!=-1:hCodeDelistingDate[code]=DelistingDate
        hCodeDateActualTradableShare[code]={}
        hCodeIndus[code]=Indus
        sDate=sorted(hDateTradableShares)
        sDate2=sorted(hDateDetailsOfshareHolders,reverse=True)
        for date in sDate:#对于每一个股本变化日，查询这个date之前的股东明细，作为当期的股东明细
            TradableShares=hDateTradableShares[date]
            try:
                date2=filter(lambda date2:date2<=date,sDate2).__next__()
                Details=hDateDetailsOfshareHolders[date2]
                ShareWhichIsStable=0
                for detail in Details:
                    num_of_shares,name_of_shareholder,kind_of_shareholder=detail
                    if (kind_of_shareholder=='国有股') or (name_of_shareholder in sActualController):
                        ShareWhichIsStable+=num_of_shares
                if TradableShares>ShareWhichIsStable:
                    hCodeDateActualTradableShare[code][date]=TradableShares-ShareWhichIsStable
            except:
                hCodeDateActualTradableShare[code][date]=TradableShares
    return(hCodeDateActualTradableShare,hCodeIndus,hCodeDelistingDate)


def main(endT,nums_of_td):
    sCode=get_sCode()
    # sCode=['300372']
    # sCode=['300305']
    # sCode=['600309']
    # sCode=['601607']
    sSUBsCode=divide_to_subsCode(sCode,nums_of_td)
    q=queue.Queue()
    sTD=[]
    print('downloading data from ibay')
    time1=time.time()
    for i in range(len(sSUBsCode)):sTD.append(td.Thread(target=td_do,args=(sSUBsCode[i],q,endT)))
    for td_ in sTD:td_.start()
    for td_ in sTD:td_.join()
    time2=time.time()
    print('downloading data takes time {}seconds'.format(time2-time1))
    print('dealing with data from ibay')
    hCodeDateActualTradableShare,hCodeIndus,hCodeDelistingDate=dealWithInfo(q)
    time3=time.time()
    print('dealing data takes time {}seconds'.format(time3-time2))
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDateActualTradableShare.txt','w')as f:pickle.dump(hCodeDateActualTradableShare,f)
    with open('E:\pyProjectData\MultiFactor\Data/hCodeIndus.txt','w')as f:pickle.dump(hCodeIndus,f)
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDelistingDate.txt','w')as f:pickle.dump(hCodeDelistingDate,f)
    return 0


main(20190601,24)
