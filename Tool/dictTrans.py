def NestDictTransfer(hKey1Key2Info):
    #hKey1Key2Info-->hKey2Key1Info
    hKey2Key1Info={}
    for key1 in hKey1Key2Info:
        hSub=hKey1Key2Info[key1]
        for key2 in hSub:
            try:
                hKey2Key1Info[key2][key1]=hSub[key2]
            except:
                hKey2Key1Info[key2]={}
                hKey2Key1Info[key2][key1]=hSub[key2]
    return(hKey2Key1Info)