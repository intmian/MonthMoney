#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

import json
from unicodedata import name

# 从图片中读取账本数据
def getPic(accounts,invests, path):
    accountValue = {}
    investValue = {}
    accountNameList = []
    for account in accounts:
        accountNameList.append(account['name'])

    import easyocr
    reader = easyocr.Reader(['ch_sim','en'],gpu=False,verbose=False)
    texts = reader.readtext(path,detail=0)
    readNext = False
    strNext = ""
    nextRead = ""
    # 如果单个字符串为-或一，替换为-，并与下一个字符串合并
    for i in range(len(texts)):
        if texts[i] == '-' or texts[i] == '一':
            if i+1 < len(texts):
                texts[i] = '-'+texts[i+1]
    for text in texts:
        if text in accountNameList:
            readNext = True
            strNext = text
            nextRead = "accounts"
            continue
        
        if text in invests:
            readNext = True
            strNext = text
            nextRead = "invests"
            continue

        if readNext:
            if nextRead == "accounts":
                text = text.replace(',','')
                text = text.replace('一','-')
                needsub = False
                if text[0] == '-':
                    needsub = True
                    text = text[1:]
                accountValue[strNext] = float(text)
                if needsub:
                    accountValue[strNext] = -accountValue[strNext]
                readNext = False
                continue
            if nextRead == "invests":
                text = text.replace(',','')
                text = text.replace('一','-')
                if text[0] == '-':
                    needsub = True
                    text = text[1:]
                accountValue[strNext] = float(text)
                if needsub:
                    accountValue[strNext] = -accountValue[strNext]
                investValue[strNext] = float(text)
                readNext = False
                continue
    return accountValue,investValue

# 获得文件夹下所有图片
def getPicList(path):
    import os
    picList = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.png' or os.path.splitext(file)[1] == '.PNG' or os.path.splitext(file)[1] == '.JPG' or os.path.splitext(file)[1] == '.jpeg' :
                picList.append(os.path.join(root, file))
    return picList

def delPicList(path):
    import os
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.png' or os.path.splitext(file)[1] == '.PNG' or os.path.splitext(file)[1] == '.JPG' or os.path.splitext(file)[1] == '.jpeg':
                os.remove(os.path.join(root, file))

def main():
    # 将当前文件夹设为运行目录
    import os
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with open(r'setting.json') as f:
        data = json.load(f)
        accountLogicMoney = {}
        accounts = data['accounts']
        accountValue = {}
        invests = data['invests']
        investValue = {}
        pacList = getPicList('./')
        print("从图片中读取账本数据:",pacList)
        print("--------------------------------------------")
        for pic in pacList:
            TempAccountValues,TempInvestValues = getPic(accounts,invests, pic)
            for TempAccountValue in TempAccountValues:
                if TempAccountValue not in accountValue:
                    accountValue[TempAccountValue] = TempAccountValues[TempAccountValue]
            for TempInvestValue in TempInvestValues:
                if TempInvestValue not in investValue:
                    investValue[TempInvestValue] = TempInvestValues[TempInvestValue]
        
        print("清除图片:",pacList)
        print("--------------------------------------------")
        delPicList('./')
        
        # 展示账本数据
        for value in accountValue:
            print(value,"的账面值:",accountValue[value])

        sumAccount = None
        sumAccountName = data['sumAccountName']
        sumAccountValue = 0
        for account in accounts:
            if account['name'] == sumAccountName:
                sumAccount = account

        for account in accounts:
            remainMoney = 0
            if account['name'] in accountValue:
                remainMoney = accountValue[account['name']]
            else:
                remainMoney = input('请输入{}的账面值：'.format(account['name']))
                remainMoney = float(eval(remainMoney))
            
            if account['debt']:
                remainMoney = -remainMoney
            if account['name'] == sumAccountName:
                sumAccountValue = remainMoney
            else:
                accountLogicMoney[account['name']] = remainMoney
            

        print("--------------------------------------------")
        for account in accounts:
            if account['name'] == sumAccountName:
                continue
            realMoney = input('请输入{}的实际值：'.format(account['name']))
            if realMoney == "":
                realMoney = accountLogicMoney[account['name']]
            else:
                realMoney = float(eval(realMoney))
            if account['debt']:
                realMoney = -realMoney

            accountLogicMoney[account['name']] = realMoney - accountLogicMoney[account['name']]
            accountLogicMoney[account['name']] = round(accountLogicMoney[account['name']], 2)
        print("--------------------------------------------")
        for account in accounts:
            if account['name'] == sumAccountName:
                continue
            if accountLogicMoney[account['name']] < 0:
                print(account['name'], '->', sumAccountName, ':', -accountLogicMoney[account['name']])
                sumAccountValue += -accountLogicMoney[account['name']]
            if accountLogicMoney[account['name']] > 0:
                print(sumAccountName, '->', account['name'], ':', accountLogicMoney[account['name']])
                sumAccountValue -= accountLogicMoney[account['name']]

        print("--------------------------------------------")

        realSumMoney = input('请输入{}的实际：'.format(sumAccountName))
        if realSumMoney == "":
            realSumMoney = sumAccountValue
        realSumMoney = float(eval(realSumMoney))

        print("--------------------------------------------")

        ChangeSumMoney = realSumMoney - sumAccountValue
        ChangeSumMoney = round(ChangeSumMoney, 2)
        if ChangeSumMoney < 0:
            print(sumAccountName, '未知去向支出', -ChangeSumMoney)
        if ChangeSumMoney > 0:
            print(sumAccountName, '未知来源收入', ChangeSumMoney)

        print("--------------------------------------------")
        # 展示投资数据
        for value in investValue:
            print(value,"的账面值:",investValue[value])
        for investName in invests:
            if investName in investValue:
                pass
            else:
                money = input('请输入{}的账面值：'.format(investName))
                money = float(eval(money))
                investValue[investName] = money
        print("--------------------------------------------")
        investRealMoneyMap = {}
        for investName in invests:
            money = input('请输入{}的实际值：'.format(investName))
            if money == "":
                money = investValue[investName]
            money = float(eval(money))
            investRealMoneyMap[investName] = money
        print("--------------------------------------------")
        for investName in invests:
            change = investRealMoneyMap[investName] - investValue[investName]
            change = round(change, 2)
            if change < 0:
                print(investName, '亏损', -change)
            if change > 0:
                print(investName, '盈利', change)
        print("--------------------------------------------")
        for investName in invests:
            realSumMoney += investRealMoneyMap[investName]
        print("总资产:",realSumMoney)
        input('按任意键退出')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        input('按任意键退出')