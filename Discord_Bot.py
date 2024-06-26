import os
import sys
import time
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from discord.ext import tasks
import re
import json
import requests
from dotenv import load_dotenv

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑
load_dotenv()

BOT_SEND_CHENNEL_ID=os.getenv('BOT_SEND_CHENNEL_ID')
DISCORD_BOT_APIKEY=os.getenv('DISCORD_BOT_APIKEY')

def System_Commend(message,commend):
    if re.search(r'add ',commend):
        return AddNewUser(commend.split(' ')[1])
    elif re.search(r'addcf ',commend):
        return AddNewUser_cf(commend.split(' ')[1])
    elif commend=='list':
        return ListAllUsers(commend)
    else:
        return '稽查程序出錯'


############ CSES part ############
def AddNewUser(userID):
    userName=Get_UserName(userID)
    Add_Database(userID)
    return "successfully add "+userName + "!"

def ListAllUsers(commend):
    return_message=""

    loadData=Load_JSON_Data()
    for(i, data) in enumerate(loadData):
            return_message+= "勇者 " + data['userName'] + " 至今已成功攻略 "+ str(len(data['problems'])) + " 個 CSES 地下城!\n"
    
    return return_message

def Load_JSON_Data():
    if os.path.exists("database.json") and os.path.getsize("./database.json") > 0:
        with open("database.json", 'r') as json_file:
            loadData = json.load(json_file)
    else:
        loadData=[]
    return loadData

def Save_JSON_Data(SavedData):
    with open("database.json", 'w') as json_file:
        json.dump(SavedData, json_file, indent=4)

def Get_UserName(userID):
    if not userID.isdigit():
        return "Not Found"

    url="https://cses.fi/user/" + userID
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    h1_tag = soup.find('h1')
    h1_content = h1_tag.text
    userName=h1_content.split(' ')[1]

    return userName

def Get_Problem_AcceptedNumber(problemName):
    url="https://cses.fi/problemset/list/"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找名称为 "Distinct Numbers" 的 <a> 标签
    distinct_numbers_a = soup.find('a', string=problemName)
    distinct_numbers_li = distinct_numbers_a.parent
    detail_span = distinct_numbers_li.find('span', class_='detail')
    return detail_span.get_text(strip=True)

def Add_Database(userID):
        url = 'https://cses.fi/problemset/user/' + userID + '/'

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=860831b610cfe3b054d3f24d4d740dcd522392b9',
            'Host': 'cses.fi',
            'Referer': 'https://cses.fi/user/229418',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有 class 为 'task-score icon full' 的 <a> 元素，并提取它们的 title 属性
        elements = soup.find_all('a', class_='task-score icon full')
        acceped_ProblemList = [element['title'] for element in elements]

        newData = {
        "userID": userID,
        "userName": Get_UserName(userID),
        "problems": acceped_ProblemList
        }

        loadData=Load_JSON_Data()
        flag=0
        for(i, data) in enumerate(loadData): # 如果 userID 已經存在, 則更新其資料
            if data['userID'] == userID:
                loadData[i]=newData
                flag=1
                break

        if flag==0:
            loadData.append(newData)

        Save_JSON_Data(loadData)

        return newData

@tasks.loop(seconds=180.0) #每180秒執行一次
async def Time_Check():
    try:
        loadData=Load_JSON_Data()
        for(i, data) in enumerate(loadData):
                oldLen=len(data['problems'])
                newData=Add_Database(data['userID'])
                newLen=len(newData['problems'])

                if newLen>oldLen: # 找出新增的那個 problems 名稱
                    newProblems=[x for x in newData['problems'] if x not in data['problems']]
                    acceped_number=Get_Problem_AcceptedNumber(newProblems[0])
                    # 102979 / 107828 分割出兩個數字
                    acceped_number=acceped_number.split(' / ')

                    message=""
                    if int(acceped_number[0])<1000:
                        message="重要公告! 勇者 " + newData['userName'] + " 成功攻略了一座新的超高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有極少數的 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<3000:
                        message="重要公告! 勇者 " + newData['userName'] + " 成功攻略了一座新的高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有少數的 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<5000:
                        message="重要公告! 勇者 " + newData['userName'] + " 成功攻略了一座新的中階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<10000:
                        message="重要公告! 勇者 " + newData['userName'] + " 成功攻略了一座新的初階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    else:
                        message="重要公告! 勇者 " + newData['userName'] + " 成功攻略了一座新的見習 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"

                    channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                    await channel.send(message)
    except:
        # 印出錯誤原因
        channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        await channel.send(sys.exc_info()[0])
############ CSES part ############
def AddNewUser_cf(userName):
    Add_Database_cf(userName)
    return "successfully add "+userName + "!"


def Load_JSON_Data_cf():
    if os.path.exists("database_cf.json") and os.path.getsize("./database_cf.json") > 0:
        with open("database_cf.json", 'r') as json_file:
            loadData = json.load(json_file)
    else:
        loadData=[]
    return loadData

def Save_JSON_Data_cf(SavedData):
    with open("database_cf.json", 'w') as json_file:
        json.dump(SavedData, json_file, indent=4)

def Add_Database_cf(userName):
    # 設置 API URL，這裡的 handle 是使用者的名字
    url = f"https://codeforces.com/api/user.info?handles={userName}"
    
    # 發送 GET 請求
    response = requests.get(url)
    
    # 解析回應的 JSON 資料
    data = response.json()
    
    # 檢查是否成功取得資料
    if data['status'] == 'OK':
        user_info = data['result'][0]
        rating = user_info.get('rating', 'No rating available')

        # 寫入資料庫
        loadData=Load_JSON_Data_cf()
        flag=0
        for(i, data) in enumerate(loadData): # 如果 userName 已經存在, 則更新其資料
            if data['userName'] == userName:
                loadData[i]['rating']=rating
                flag+=1
                break

        if flag==0: # 如果 userName 不存在, 則新增一筆資料
            newData = {
            "userName": userName,
            "rating": rating
            }
            loadData.append(newData)

        Save_JSON_Data_cf(loadData)
        return rating
    else:
        return -1



@tasks.loop(seconds=180.0) #每180秒執行一次
async def Time_Check_cf():
    try:
        loadData=Load_JSON_Data_cf()
        for(i, data) in enumerate(loadData):
            oldRating=data['rating']
            newRating=Add_Database_cf(data['userName'])
            if newRating!=-1 and newRating!=oldRating:
                if newRating>oldRating:
                    message="勇者 " + data['userName'] + " 展現了他無與倫比的勇氣和智慧，成功攻略了危險重重的地下城! 為了表揚其英勇事蹟，其積分從 " + str(oldRating) + " 上升至 " + str(newRating) + "，共提升了 " + str(newRating-oldRating) + " 分!"
                else:
                    message="勇者 " + data['userName'] + " 這次的地下城攻略行動並不順利，我們很遺憾的表示，該勇者的積分將從 " + str(oldRating) + " 下降至 " + str(newRating) + "，共下降了 " + str(oldRating-newRating) + " 分!"

                channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                await channel.send(message)
            time.sleep(3)
    except:
        print(sys.exc_info()[0])

############ CSES part ############



@client.event
async def on_ready(): #啟動成功時會呼叫
    try:
        channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID)) # 用頻道ID定位想要發送訊息的那個頻道
        await channel.send('**[System]** bot成功啟動!')
        await channel.send('進入稽查模式')
    except Exception as e:
        # 印出錯誤原因
        channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        await channel.send(str(e))

    Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式
    Time_Check_cf.start()

@client.event
async def on_message(message): #有新的訊息便會呼叫
    try:
        if message.author == client.user: #若新訊息是bot本身則忽略
            return
        elif message.content[:12]=='System call ':
            commend=message.content[12:]

            sendMessage=System_Commend(message,commend)
            print(sendMessage)
            client._connection._messages.clear()
            await message.channel.send(sendMessage)
    except Exception as e:
        # 印出錯誤原因
        channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        await channel.send(str(e))

client.run(DISCORD_BOT_APIKEY) #啟動bot
