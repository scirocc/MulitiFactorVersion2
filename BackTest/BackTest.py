# coding=utf-8
import glob
import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import multiprocessing as mp
class BackTestBase(object):
    def __init__(self,
                 A4s,#股票账户的实例
                 year,#要回测哪年的结果
                 strategyCodeWeightGener):
        self.A4s=A4s
        self.year=year
        self.strategyCodeWeightGener=strategyCodeWeightGener
        sFile = sorted(glob.glob('../Data/dayline/*'))
        sDate=[file[-8:-4] for file in sFile]
        if year: sDate = list(filter(lambda date:date[-8:-4]==year , sDate))
        self.sDate=sDate
        self.dayMarket=None


    def ReadDayMarket(self,sonConn):
        while True:
            date=sonConn.recv()
            if date:
                with open('../Data/dayline/hCodeInfoOf{}'.format(date), 'rb')as f: hCodeInfo = pickle.load(f)
                sonConn.send(hCodeInfo)
            else:
                sonConn.close()

    #多进程函数
    def backtestAsGenerator(self):
        fatherConn,sonConn=mp.Pipe()
        readProcess=mp.Process(target=self.ReadDayMarket,args=(sonConn,))#声明独立读取的异步函数
        readProcess.start()
        sNet=[]
        for j, date in enumerate(self.sDate):
            if j == 1:  #如果是第一天的话，那么缓冲两天的数据
                todayDate=oldDate
                nextDate=date
                fatherConn.send(todayDate)
                self.dayMarket=fatherConn.recv()
                fatherConn.send(nextDate)
                slicingInfo = self.dayMarket
                net = self.A4s.SliceingInfoAccepter.send(slicingInfo, todayDate)  # 发送
                sNet.append(net)
            elif j:#若是其他的日期那么就缓冲一天就可以了
                todayDate=oldDate
                self.dayMarket = fatherConn.recv()
                fatherConn.send(date)
                slicingInfo = self.dayMarket
                net = self.A4s.SliceingInfoAccepter.send(slicingInfo, todayDate)  # 发送
                sNet.append(net)
            oldDate=date
        #然后再收最后一天的行情并发送结束标志，终止pipe
        self.dayMarket = fatherConn.recv()
        fatherConn.send(0)
        slicingInfo = self.dayMarket
        net = self.A4s.SliceingInfoAccepter.send(slicingInfo, date)  # 发送
        sNet.append(net)
        readProcess.join()
        return(sNet)










    def sNetAnalysis(self,sNet):
        dayReturn=pow(sNet[-1],1/len(sNet)) #日均收益
        yearReturn=pow(dayReturn,244)-1     #年化收益
        daySigma=np.std(sNet)               #日均波动率
        yearSigma=244**0.5*daySigma
        sharp=yearReturn/yearSigma
        return(yearReturn,sharp)
    #
    def paintingConfig(self,sDate,sNet,nameOfPainting,interval='day'):
        if interval=='month':interval=20
        elif interval=='quarter':interval=60
        elif interval=='year':interval=244
        else:interval=1
        sX=list(len(sNet))
        floor=sX[0]
        ceil=sX[-1]
        sMy_scale = np.arange(floor, ceil, interval)
        sDateAdjust=[sDate[sX.index(x)] for x in sMy_scale]
        plt.plot(sX,sNet,lable=nameOfPainting)
        plt.xticks(sMy_scale,sDateAdjust,rotation=60)
        return 0
    #
    def draw(self,yearReturn,sharp):
        plt.title('yearReturn:{}.yearSharp:{}'.format(yearReturn,sharp))
        plt.show()