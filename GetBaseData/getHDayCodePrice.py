# coding=utf-8
import glob,pickle


def main():
    sFile = glob.glob('../Data/dayline/*')
    hDateCodeInfo={}
    def dealfunc(file):
        with open(file,'rb')as f:hCodeInfo=pickle.load(f)
        hDateCodeInfo[file[-8:]]=hCodeInfo
        return 0
    list(map(dealfunc,sFile))
    hDayCodePrice={date:{code:info[-2]} for date,hCodeInfo in hDateCodeInfo.items() for code,info in hCodeInfo.items()}
    return(hDayCodePrice)
