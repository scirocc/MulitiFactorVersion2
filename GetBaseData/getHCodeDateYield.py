# coding=utf-8

import json,datetime

def main():
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDelistingDate.txt','r')as f:
        hCodeDelistingDate=json.load(f)
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDatePrice.txt','r')as f:
        hCodeDatePrice=json.load(f)
    hCodeDateYield={}
    sDate=[]
    for code in hCodeDatePrice:
        sDate.extend(hCodeDatePrice[code].keys())
    sDate=sorted(set(sDate))
    #生成sEndT
    days=20
    sEndT=[int(sDate[0])]
    for i in range(int(len(sDate)/days)):
        sEndT.append(int(sDate[days*i+days]))
    for code in hCodeDatePrice:
        hCodeDateYield[code]={}
        sDate=sorted(hCodeDatePrice[code],reverse=True)
        sDate=[int(x) for x in sDate]
        try:DelistingDate=hCodeDelistingDate[code]
        except:DelistingDate=30000000
        for date in sEndT:
            if date<DelistingDate:
                DateOfDateformat=datetime.datetime.strptime(str(date),"%Y%m%d")
                DateSupposeToBeBeginT=int(datetime.datetime.strftime(DateOfDateformat-datetime.timedelta(days=(20)),"%Y%m%d"))
                DateSupposeToBeEndT=int(datetime.datetime.strftime(DateOfDateformat,"%Y%m%d"))
                try:
                    DateActuallyToBeBeginT=filter(lambda x:x<=DateSupposeToBeBeginT,sDate).__next__()
                    DateActuallyToBeEndT=filter(lambda x:x<=DateSupposeToBeEndT,sDate).__next__()
                    factorExpose=hCodeDatePrice[code][str(DateActuallyToBeEndT)]/\
                                 hCodeDatePrice[code][str(DateActuallyToBeBeginT)]
                    hCodeDateYield[code][date]=factorExpose
                except:
                    pass
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDateYield.txt','w')as f:
        json.dump(hCodeDateYield,f)
    return 0
main()