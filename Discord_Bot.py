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
    elif commend=='list':
        return ListAllUsers(commend)
    else:
        return '稽查程序出錯'

def AddNewUser(userID):
    userName=Get_UserName(userID)
    Add_Database(userID)
    return "successfully add "+userName + "!"

def ListAllUsers(commend):
    return_message=""

    loadData=Load_JSON_Data()
    for(i, data) in enumerate(loadData):
            return_message+=data['userName'] + " has Acceped "+ str(len(data['problems'])) + " problems!\n"
    
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

@tasks.loop(seconds=60.0) #每60秒執行一次
async def Time_Check():
    try:
        print('Time_Check')
        loadData=Load_JSON_Data()
        for(i, data) in enumerate(loadData):
                oldLen=len(data['problems'])
                newData=Add_Database(data['userID'])
                newLen=len(newData['problems'])

                if newLen>oldLen: # 找出新增的那個 problems 名稱
                    newProblems=[x for x in newData['problems'] if x not in data['problems']]
                    message="**[System]** " + newData['userName'] + " has accepted new problem: " + newProblems[0] + "\n"
                    message = message + "difficulty: " + str(Get_Problem_AcceptedNumber(newProblems[0]))

                    channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                    await channel.send(message)
    except:
        # 印出錯誤原因
        channel = discord.utils.get(client.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        await channel.send(sys.exc_info()[0])


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
