# coding=utf-8
import glob,pickle


def main():
    sFile = sorted(glob.glob('../Data/dayline/*'))
    with open('../Data/hCodeDelistingDate','rb')as f:hCodeDelistingDate=pickle.load(f)
    def dealfunc(file):
        with open(file,'rb')as f:hCodeInfo=pickle.load(f)
        return (file[-8:],hCodeInfo)
    hDateCodeInfo=dict(map(dealfunc,sFile))

    hDayCodePrice={date:{code:info[-2]} for date,hCodeInfo in hDateCodeInfo.items() for code,info in hCodeInfo.items()}
    # #把停牌时的价格按照上一交易日的价格补上


    return(hDayCodePrice)
# main()
