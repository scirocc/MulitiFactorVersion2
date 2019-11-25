# coding=utf-8
import glob,pickle,datetime


def main():
    sFile = glob.glob('../data/dayline/*')
    hDateCodeInfo={file[-8:]:pickle.load(file) for file in sFile}
    def dealData(date):
        closeprice,averPrice,volume,amount,rehabilitationClosePrice,rehabilitationAverPrice=hDateCodeInfo[date]


        pass


def MultiThreadRead(sSubSubFile,MP_QUEUE1,MP_QUEUE2):#刨除停牌的
    for file in sSubSubFile:
        hCodeDatePrice={}
        hCodeDateRealPrice={}
        with open(file,'r')as f:
            code=file[-10:-4]
            hCodeDatePrice[code]={}
            hCodeDateRealPrice[code]={}
            for line in f:
                date,c,volume, amount, change,exright_c,exright_averPrice,Todayshare=line.strip().split(',')
                hCodeDatePrice[code][int(date)]=round(float(exright_c),2)
                hCodeDateRealPrice[code][int(date)]=round(float(c),2)
        MP_QUEUE1.put(hCodeDatePrice)
        MP_QUEUE2.put(hCodeDateRealPrice)
    return 0

def MultiProcessArrangement(sSubFile,MP_QUEUE1,MP_QUEUE2,numsOfTD_PerMP,e,nums_of_file):
    sSubSubFile=divide_to_sub_sFile(sSubFile,numsOfTD_PerMP)
    sTD=[]
    for i in range(len(sSubSubFile)):sTD.append(td.Thread(target=MultiThreadRead,args=(sSubSubFile[i],MP_QUEUE1,MP_QUEUE2)))
    for td_ in sTD:td_.start()
    for td_ in sTD:td_.join()
    if MP_QUEUE1.qsize()==MP_QUEUE2.qsize()==nums_of_file:e.set()
    return 0

def divide_to_sub_sFile(sFile,num_of_mp):
    whole_nums=len(sFile)
    sSUBsFile=[sFile[slice(i,whole_nums,num_of_mp)] for i in range(num_of_mp)]
    return(sSUBsFile)


def main():
    sFile=glob.glob('E:\pyProjectData\MultiFactor\Data\stockDayLine/*.csv')
    nums_of_file=len(sFile)
    nums_of_mp=mp.cpu_count()
    sSUBsFile=divide_to_sub_sFile(sFile,nums_of_mp)
    numsOfTD_PerMP=2
    MP_QUEUE1=mp.Queue()
    MP_QUEUE2=mp.Queue()
    sMP=[]
    time1=datetime.datetime.now()
    e=mp.Event()
    for i in range(len(sSUBsFile)):sMP.append(
        mp.Process(target=MultiProcessArrangement,args=(sSUBsFile[i],MP_QUEUE1,MP_QUEUE2,numsOfTD_PerMP,e,nums_of_file)))
    for mp_ in sMP:
        mp_.start()
        print(sMP.index(mp_),'is running')
    e.wait()
    time2=datetime.datetime.now()
    print('读取+整理文件花费',time2-time1)
    hCodeDatePrice={}
    hCodeDateRealPrice={}
    for i in range(nums_of_file):#要养成习惯把queue中元素押出栈，不然主函数永远挂起
        h1=MP_QUEUE1.get()
        h2=MP_QUEUE2.get()
        hCodeDatePrice.update(h1)
        hCodeDateRealPrice.update(h2)
    #json three dict
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDatePrice.txt','w')as f:json.dump(hCodeDatePrice,f)
    with open('E:\pyProjectData\MultiFactor\Data/hCodeDateRealPrice.txt','w')as f:json.dump(hCodeDateRealPrice,f)
    return 0

if __name__=="__main__":
    main()