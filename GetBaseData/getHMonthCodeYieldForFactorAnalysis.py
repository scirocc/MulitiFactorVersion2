# coding=utf-8

import pickle
from functools import reduce

def main(hDayCodePrice):
    sDate=sorted(hDayCodePrice)
    #生成sEndT
    sEndT=sDate[slice(0,len(sDate),20)]
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    hMonthCodeYield={}
    def dealfunc(oldDate,Date):
        hCodePrice1 = hDayCodePrice[oldDate]
        hCodePrice2 = hDayCodePrice[Date]
        hCodeYield={}
        for code in hCodePrice2:
            try:
                price1=hCodePrice1[code]
                price2=hCodePrice2[code]
                Yield=round(price2/price1,3)
                hCodeYield[code]=Yield
            except:
                pass
        hMonthCodeYield[Date]=hCodeYield
        return(Date)
    reduce(dealfunc,sEndT)
    with open('../Data/hMonthCodeYield','wb')as f:
        pickle.dump(hMonthCodeYield,f)
    return 0
