# coding=utf-8
import glob,copy
import pickle
import numpy as np
class Account4s(object):
    def __init__(self,Initial_balance,StrategyIntance,fee=0.002):
        #sDate为回测日期范围
        self.hSliceingInfo=0#c,aver,vol,amount,re_c,re_aver
        self.StrategyIntance=StrategyIntance
        self.fee=fee
        self.profit=0
        self.Avilable_balance=Initial_balance
        self.now_account_balance_of_stock=0#持仓股票市值
        #再update仓位的时候自动更新持仓份额，按照reweightfactor重构
        self.sPosition=[]#标的名称,开仓时点，开仓时价格，现持仓份额，除权后现价
        ################################################################################################################################################################
        ################################################################################################################################################################

    def getPrice(self,code):
        return(self.hSliceingInfo[code][0])

    def UpdateAccountInfo(self):
        sliceingInfo=self.hSliceingInfo
        for holding in self.sPosition:
            code,openTime,openPrice,Share,Price=holding
            valueBeforeUpdate=Price*Share
            Info4code=sliceingInfo[code]
            RF_Rate=Info4code[-1]
            nowPrice=Info4code[1]
            nowShare=Share*RF_Rate
            valueAfterUpdate=nowPrice*nowShare
            profit=valueAfterUpdate-valueBeforeUpdate
            self.profit+=profit
            self.now_account_balance_of_stock += profit
            holding[-2:]=nowShare,nowPrice#修改持仓信息
        return (0)

    def sliceingInfoAccepter(self):
        while True:
            self.aSliceingInfo,date = yield  # 由BackTest类传递过来
            #每收到一个slicingInfo都第一时间更新账户情况
            self.UpdateAccountInfo()
            hCodeWeight=self.StrategyIntance.planGenner.send(self.aSliceingInfo,self.sPosition)
            if hCodeWeight:#不为空的话说明有新的持仓计划
                self.AdjustWarehouseAsPlan(hCodeWeight,date)#time的前8位是date
            yield self.Avilable_balance+self.now_account_balance_of_stock#把net再发回去


    def buy4CertainAmount(self, code, AmountExpectToBuy, date):
        price = self.getPrice(code)
        share_ceil = min(self.Avilable_balance, AmountExpectToBuy * (1 + self.fee)) / (price * (1 + self.fee))
        share_ceil = np.floor(share_ceil / 100) * 100  # 一手为单位
        if share_ceil > 0:
            moneyNeeding = share_ceil * price * (1 + self.fee)
            self.profit -= moneyNeeding * self.fee / (1 + self.fee)  # 更新持仓利润
            self.now_account_balance_of_stock += moneyNeeding / (1 + self.fee)  # 更新现持仓实际价值
            self.Avilable_balance -= moneyNeeding  # 更新可用金额、
            self.sPosition.append([code, date,price,share_ceil, price])#标的名称,开仓时点，开仓时价格，现持仓份额，除权后现价
        return 0

    def sell4CertainAmount(self,code,AmountExpectToSell,date):#在更新完今天仓位后运行
        priceNow = self.getPrice(code)
        positions=copy.deepcopy(self.sPosition)
        sHolding=[holding for holding in positions if holding[0]==code and holding[1]!=date]
        ShareExpectToSell=round(AmountExpectToSell/priceNow)*priceNow
        for holding in sHolding:#标的名称,开仓时点，除权后现持仓份额，除权后现价
            shares=holding[-2]
            if shares>=ShareExpectToSell:
                self.Avilable_balance+=ShareExpectToSell*priceNow#更新可用资金
                shares_left=shares-ShareExpectToSell
                self.now_account_balance_of_stock -= ShareExpectToSell * priceNow
                self.sPosition.remove(holding)#更新持仓
                if shares_left>0:
                    self.sPosition.append([holding[0],holding[1],holding[2],shares_left,priceNow])
                break
            else:
                self.sPosition.remove(holding)
                self.now_account_balance_of_stock -= shares*priceNow
                self.Avilable_balance+=shares*priceNow
                ShareExpectToSell-=shares
        return 0

    def getHCodeWeightNow(self):
        hCodeWeightNow={}
        allAvilableMoney=self.now_account_balance_of_stock+self.Avilable_balance
        def dealFunc(position):
            code, openDate, priceWhenOpen, share, price = position
            percent = share * price / allAvilableMoney
            try:hCodeWeightNow[code] += percent
            except:hCodeWeightNow[code] = percent
        list(map(dealFunc,self.sPosition))
        return(hCodeWeightNow,allAvilableMoney)
    #
    def AdjustWarehouseAsPlan(self,hCodeWeightTarget,date):#执行持仓计划
        hCodeWeightNow,allAvilableMoney=self.getHCodeWeightNow()
        #注意这里的坑，应该优先处理要卖的，再处理要买的，否则可用资金永远是0
        def func4sell(code):
            try:WeightTarget=hCodeWeightTarget[code]
            except:WeightTarget=0
            try:WeightNow=hCodeWeightNow[code]
            except:WeightNow=0
            WeightChange=WeightTarget-WeightNow
            if WeightChange<0:
                AmountExpectToSell=allAvilableMoney*(-1)*WeightChange
                self.sell4CertainAmount(code,AmountExpectToSell,date)
        list(map(func4sell,hCodeWeightNow))
        def fun4buy(code):
            try:WeightTarget=hCodeWeightTarget[code]
            except:WeightTarget=0
            try:WeightNow=hCodeWeightNow[code]
            except:WeightNow=0
            AmountExpectToExecute=(WeightTarget-WeightNow)*allAvilableMoney
            if AmountExpectToExecute>0:
                self.buy4CertainAmount(code, AmountExpectToExecute, date)
        list(map(fun4buy,hCodeWeightTarget))
        return 0
