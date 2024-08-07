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

bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()

BOT_SEND_CHENNEL_ID=os.getenv('BOT_SEND_CHENNEL_ID')
DISCORD_BOT_APIKEY=os.getenv('DISCORD_BOT_APIKEY')

@bot.slash_command(name="ping", description="測試指令")
async def ping(ctx):
    embed=discord.Embed(title="Pong!", description="目前機器人延遲為 " + str(round(bot.latency*1000)) + "ms", color=0x00ff00)
    await ctx.respond(embed=embed)
@bot.slash_command(name="help", description="列出所有指令")
async def help(ctx):
    # using Embed
    embed=discord.Embed(title="指令列表", description="以下是所有指令的列表", color=0x00ff00)
    embed.add_field(name="add [userID]", value="新增一位CSES使用者", inline=False)
    embed.add_field(name="addcf [userName]", value="新增一位Codeforces使用者", inline=False)
    embed.add_field(name="list", value="列出所有CSES使用者", inline=False)
    embed.add_field(name="listcf", value="列出所有Codeforces使用者", inline=False)
    embed.add_field(name="delete [userID]", value="刪除一位CSES使用者", inline=False)
    embed.add_field(name="deletecf [userName]", value="刪除一位Codeforces使用者", inline=False)
    embed.add_field(name="help", value="列出所有指令", inline=False)
    embed.add_field(name="ping", value="測試指令", inline=False)
    await ctx.respond(embed=embed)

async def commnad_response(ctx, type, message):
    if type == "Error":
        embed=discord.Embed(title="Error", description=message, color=0xEA0000)
    elif type == "Success":
        embed=discord.Embed(title="Success", description=message, color=0x00EC00)
    else:
        embed=discord.Embed(title="Notify", description=message, color=0x0080FF)
    await ctx.respond(embed=embed)

############ CSES part ############
@bot.slash_command(name="add", description="新增一位CSES使用者")
async def add(ctx, user_id: discord.Option(str)):
    userName = Get_UserName(user_id)
    ret = Add_Database(user_id)
    if userName == "Not Found":
        await commnad_response(ctx, "Error", "Failed to add " + user_id + " because the user does not exist!")
    elif ret == False:
        await commnad_response(ctx, "Error", "Failed to add " + user_id + " because the user does not exist!")
    else:
        await commnad_response(ctx, "Success", "successfully add "+userName + "!")

@bot.slash_command(name="list", description="列出所有CSES使用者")
async def list(ctx):
    embed = discord.Embed(title="CSES冒險者列表", description="列出所有 CSES 使用者", color=0x0080FF)
    loadData=Load_JSON_Data()
    for(i, data) in enumerate(loadData):
        embed.add_field(name="勇者 " + data['userName'], value="成功攻略 "+ str(len(data['problems'])) + " 個 CSES 地下城", inline=True)
    await ctx.respond(embed=embed)

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

@bot.slash_command(name="delete", description="刪除一位CSES使用者")
async def delete(ctx, user_id: discord.Option(str)):
    loadData=Load_JSON_Data()
    flag = 0
    for(i, data) in enumerate(loadData):
        if data['userID'] == user_id:
            del loadData[i]
            flag += 1
            break
    Save_JSON_Data(loadData)
    if flag == 0:
        await commnad_response(ctx, "Error", "Failed to delete " + user_id + " because the user does not exist!")
    else:
        await commnad_response(ctx, "Success", "successfully delete "+ user_id + "!")

def Get_Problem_AcceptedNumber(problemName):
    url="https://cses.fi/problemset/list/"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

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

        # if get 443, then return
        if soup.find('h1').text == 'Not Found':
            return False

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
                        message="勇者 " + newData['userName'] + " 成功攻略了一座新的超高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有極少數的 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<3000:
                        message="勇者 " + newData['userName'] + " 成功攻略了一座新的高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有少數的 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<5000:
                        message="勇者 " + newData['userName'] + " 成功攻略了一座新的中階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    elif int(acceped_number[0])<10000:
                        message="勇者 " + newData['userName'] + " 成功攻略了一座新的初階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"
                    else:
                        message="勇者 " + newData['userName'] + " 成功攻略了一座新的見習 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位勇者成功走到了最後!"

                    channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                    embed = discord.Embed(title="地下城攻略成功公告", description=message, color=0x00EC00)
                    await channel.send(embed=embed)
    except:
        # 印出錯誤原因
        channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        await channel.send(sys.exc_info()[0])
############ Codeforces part ############
@bot.slash_command(name="addcf", description="新增一位Codeforces使用者")
async def addcf(ctx, user_name: str):
    ret = Add_Database_cf(user_name)
    if ret == -1:
        await commnad_response(ctx, "Error", "Failed to add " + user_name + " because the user does not exist!")
    else:
        await commnad_response(ctx, "Success", "successfully add "+ user_name + "!")

@bot.slash_command(name="listcf", description="列出所有Codeforces使用者")
async def listcf(ctx):
    embed = discord.Embed(title="Codeforces冒險者列表", description="列出所有 Codeforces 使用者", color=0x0080FF)
    loadData=Load_JSON_Data_cf()
    for(i, data) in enumerate(loadData):
        embed.add_field(name="勇者 " + data['userName'], value="積分為 "+ str(data['rating']), inline=True)
    await ctx.respond(embed=embed)

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

@bot.slash_command(name="deletecf", description="刪除一位Codeforces使用者")
async def deletecf(ctx, user_name: discord.Option(str)):
    loadData=Load_JSON_Data_cf()
    flag = 0
    for(i, data) in enumerate(loadData):
        if data['userName'] == user_name:
            del loadData[i]
            flag += 1
            break
    Save_JSON_Data_cf(loadData)
    if flag == 0:
        await commnad_response(ctx, "Error", "Failed to delete " + user_name + " because the user does not exist!")
    else:
        await commnad_response(ctx, "Success", "successfully delete "+ user_name + "!")

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
                    embed = discord.Embed(title="Codeforces地下城公告", description=message, color=0x00EC00)
                else:
                    message="勇者 " + data['userName'] + " 這次的地下城攻略行動並不順利，我們很遺憾的表示，該勇者的積分將從 " + str(oldRating) + " 下降至 " + str(newRating) + "，共下降了 " + str(oldRating-newRating) + " 分!"
                    embed = discord.Embed(title="Codeforces地下城公告", description=message, color=0xEA0000)
                channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                await channel.send(embed=embed)
    except:
        print(sys.exc_info()[0])

############ Codeforces part ############

@bot.event
async def on_ready(): #啟動成功時會呼叫
    try:
        channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID)) # 用頻道ID定位想要發送訊息的那個頻道
        embed = discord.Embed(title="[System]", description="bot成功啟動!", color=0x00EC00)
        embed.add_field(name="指令前綴", value="/", inline=False)
        await channel.send(embed=embed)
    except Exception as e:
        # 印出錯誤原因
        channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
        embed = discord.Embed(title="Error", description=sys.exc_info()[0], color=0xEA0000)
        await channel.send(embed=embed)

    Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式
    Time_Check_cf.start()

@bot.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == bot.user:
        return
    elif "Sys call" in message.content:
        await message.channel.send("現在改用斜線指令瞜，請用 `/` 作為指令前綴!")

bot.run(DISCORD_BOT_APIKEY) #啟動bot
