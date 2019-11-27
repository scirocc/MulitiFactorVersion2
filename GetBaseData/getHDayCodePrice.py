# coding=utf-8
import glob,pickle


def main():
    sFile = sorted(glob.glob('../Data/dayline/*'))
    def dealfunc(file):
        with open(file,'rb')as f:hCodeInfo=pickle.load(f)
        return (file[-8:],hCodeInfo)
    hDateCodeInfo=dict(map(dealfunc,sFile))
    hDayCodePrice={date:{code:info[-2]} for date,hCodeInfo in hDateCodeInfo.items() for code,info in hCodeInfo.items()}
    return(hDayCodePrice)
