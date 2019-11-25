# coding=utf-8
import multiprocessing as mp
import affinity as af
import time
import psutil
import os
def divide_to_subsList(s,num_of_mp):
    whole_nums=len(s)
    sSUBsList=[s[slice(i,whole_nums,num_of_mp)] for i in range(num_of_mp)]
    return(sSUBsList)


def fun(i,sParaOfshareMemory,hResultOfshareMemo):
    print('process{} is running'.format(i+1))
    af.set_process_affinity_mask(os.getpid(),pow(2,i))# 邦核
    sSUBsList,dealFunc,sPara=sParaOfshareMemory
    sSub=sSUBsList[i]
    dealFunc(sSub,sPara,hResultOfshareMemo)
    print('process{} done'.format(i+1))
    return 0




def main(sList,dealFunc,sPara,numOfCores=psutil.cpu_count(logical = False)):
    sSUBsList=divide_to_subsList(sList,numOfCores)
    sMP=[]
    with mp.Manager() as myManger:#内部有锁，读写进程安全
        sParaOfshareMemo=myManger.list([sSUBsList,dealFunc,sPara])#使用共享内存，减少多进程启动时间
        hResultOfshareMemo=myManger.dict()#用其返回运算结果
        '''
        hResultOfshareMemo作为共享字典，在子进程修改时有坑：
        不可h[1][2]=3             !!!!
        只可subH={2:3},h[1]=subH  !!!!!!!!!!!!
        '''
        time1=time.time()
        for i in range(numOfCores):sMP.append(mp.Process(target=fun,args=(i,sParaOfshareMemo,hResultOfshareMemo)))
        for mp123 in sMP:mp123.start()
        time2=time.time()
        print('preparing multiprocess takes {} seconds'.format(time2-time1))
        for mp123 in sMP:mp123.join()
        time3=time.time()
        print('running multiprocess takes {} seconds'.format(time3-time2))
    return (hResultOfshareMemo)

def fun(hResultOfshareMemo):
    h={i:{i:i} for i in range(1000)}
    hResultOfshareMemo.update(h)
if __name__=="__main__":
    with mp.Manager() as myManger:#内部有锁，读写进程安全
        hResultOfshareMemo=myManger.dict()
        sMP=[]
        for i in range(1): sMP.append(mp.Process(target=fun, args=(hResultOfshareMemo,)))
        for mp123 in sMP: mp123.start()
        for mp123 in sMP: mp123.join()
        print(hResultOfshareMemo)