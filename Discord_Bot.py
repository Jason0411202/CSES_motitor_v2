import os
import sys
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from discord.ext import tasks
import json
import requests

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


BOT_SEND_CHENNELS_ID=""
DISCORD_BOT_APIKEY=""

@bot.slash_command(name="ping", description="與「神鷹教・對 bug 特別作戰部隊」總部前台互動")
async def ping(ctx):
    embed=discord.Embed(title="Pong!", description="您好，偉大的戰士，有什麼是我可以幫助您的嗎?", color=0x00ff00)
    embed.add_field(name="回應時間: ", value=str(round(bot.latency*1000)) + "ms", inline=False)
    await ctx.respond(embed=embed)
@bot.slash_command(name="help", description="列出所有互動方式")
async def help(ctx):
    # using Embed
    embed=discord.Embed(title="指令列表", description="以下是所有互動方式的列表", color=0x00ff00)
    embed.add_field(name="add [userID]", value="註冊一位新的 CSES 地下城挑戰者", inline=False)
    embed.add_field(name="addcf [userName]", value="註冊一位「神鷹教・對 bug 特別作戰部隊」隊員", inline=False)
    embed.add_field(name="list", value="列出所有 CSES 地下城挑戰者", inline=False)
    embed.add_field(name="listcf", value="列出所有「神鷹教・對 bug 特別作戰部隊」隊員", inline=False)
    embed.add_field(name="delete [userID]", value="註銷一位 CSES 地下城挑戰者", inline=False)
    embed.add_field(name="deletecf [userName]", value="註銷一位「神鷹教・對 bug 特別作戰部隊」隊員", inline=False)
    embed.add_field(name="help", value="列出所有互動方式", inline=False)
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
@bot.slash_command(name="add", description="註冊一位新的 CSES 地下城挑戰者")
async def add(ctx, user_id: discord.Option(str)):
    userName = Get_UserName(user_id)
    ret = Add_Database(user_id)
    if userName == "Not Found":
        await commnad_response(ctx, "Error", "註冊失敗! " + user_id + " 不存在")
    elif ret == False:
        await commnad_response(ctx, "Error", "註冊失敗! " + user_id + " 不存在")
    else:
        await commnad_response(ctx, "Success", "成功註冊挑戰者 "+userName + " !")

@bot.slash_command(name="list", description="列出所有 CSES 地下城挑戰者")
async def list(ctx):
    embed = discord.Embed(title="CSES 地下城挑戰者列表", description="列出所有 CSES 地下城挑戰者", color=0x0080FF)
    loadData=Load_JSON_Data()
    for(i, data) in enumerate(loadData):
        embed.add_field(name="挑戰者 " + data['userName'], value="成功攻略 "+ str(len(data['problems'])) + " 個 CSES 地下城", inline=True)
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

@bot.slash_command(name="delete", description="註銷一位 CSES 地下城挑戰者")
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
        await commnad_response(ctx, "Error", "註銷失敗! " + user_id + " 不存在")
    else:
        await commnad_response(ctx, "Success", "成功註銷挑戰者 "+ user_id + " !")

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
                        message="挑戰者 " + newData['userName'] + " 成功攻略了一座新的超高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有極少數的 " + acceped_number[0] + " 位挑戰者成功走到了最後!"
                    elif int(acceped_number[0])<3000:
                        message="挑戰者 " + newData['userName'] + " 成功攻略了一座新的高階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，只有少數的 " + acceped_number[0] + " 位挑戰者成功走到了最後!"
                    elif int(acceped_number[0])<5000:
                        message="挑戰者 " + newData['userName'] + " 成功攻略了一座新的中階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位挑戰者成功走到了最後!"
                    elif int(acceped_number[0])<10000:
                        message="挑戰者 " + newData['userName'] + " 成功攻略了一座新的初階 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位挑戰者成功走到了最後!"
                    else:
                        message="挑戰者 " + newData['userName'] + " 成功攻略了一座新的見習 CSES 地下城 " + newProblems[0] + "\n"
                        message = message + "截至目前為止，共有 " + acceped_number[0] + " 位挑戰者成功走到了最後!"

                    for BOT_SEND_CHENNEL_ID in BOT_SEND_CHENNELS_ID:
                        channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                        embed = discord.Embed(title="地下城攻略成功公告", description=message, color=0x00EC00)
                        await channel.send(embed=embed)
    except:
        # 印出錯誤原因
        for BOT_SEND_CHENNEL_ID in BOT_SEND_CHENNELS_ID:
            channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
            await channel.send(sys.exc_info()[0])
############ Codeforces part ############
@bot.slash_command(name="addcf", description="註冊一位「神鷹教・對 bug 特別作戰部隊」隊員")
async def addcf(ctx, user_name: str):
    ret = Add_Database_cf(user_name)
    if ret == -1:
        await commnad_response(ctx, "Error", "註冊失敗! " + user_name + " 不存在")
    else:
        await commnad_response(ctx, "Success", "成功註冊隊員 "+ user_name + "! 為大雉王獻上你的一切吧 !")

@bot.slash_command(name="listcf", description="列出所有「神鷹教・對 bug 特別作戰部隊」隊員")
async def listcf(ctx):
    embed = discord.Embed(title="「神鷹教・對 bug 特別作戰部隊」隊員列表", description="列出所有「神鷹教・對 bug 特別作戰部隊」隊員", color=0x0080FF)
    loadData=Load_JSON_Data_cf()
    for(i, data) in enumerate(loadData):
        embed.add_field(name="隊員 " + data['userName'], value="戰力為 "+ str(data['rating']), inline=True)
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

@bot.slash_command(name="deletecf", description="註銷一位「神鷹教・對 bug 特別作戰部隊」隊員")
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
        await commnad_response(ctx, "Error", "註銷失敗! " + user_name + " 不存在")
    else:
        await commnad_response(ctx, "Success", "成功註銷隊員 "+ user_name + "! 願大雉王永遠伴你左右")

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
                    message="隊員 " + data['userName'] + " 展現了他無與倫比的勇氣和智慧，成功擊退了凶險的 bug 入侵! 該隊員的戰力從 " + str(oldRating) + " 上升至 " + str(newRating) + "，共提升了 " + str(newRating-oldRating) + " 分!"
                    embed = discord.Embed(title="「神鷹教・對 bug 特別作戰部隊」 戰報", description=message, color=0x00EC00)
                else:
                    message="隊員 " + data['userName'] + " 在凶險的 bug 入侵中受了重傷，我們很遺憾的表示，該隊員的戰力從 " + str(oldRating) + " 下降至 " + str(newRating) + "，共下降了 " + str(oldRating-newRating) + " 分!"
                    embed = discord.Embed(title="「神鷹教・對 bug 特別作戰部隊」 戰報", description=message, color=0xEA0000)

                for BOT_SEND_CHENNEL_ID in BOT_SEND_CHENNELS_ID:
                    channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
                    await channel.send(embed=embed)
    except:
        print(sys.exc_info()[0])

############ Codeforces part ############

@bot.event
async def on_ready(): #啟動成功時會呼叫
    try:
        for BOT_SEND_CHENNEL_ID in BOT_SEND_CHENNELS_ID:
            channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID)) # 用頻道ID定位想要發送訊息的那個頻道
            embed = discord.Embed(title="「神鷹教・對 bug 特別作戰部隊」總部公告", description="通訊系統曾短暫受到 bug 攻擊干擾，現已恢復正常運作", color=0x00EC00)
            embed.add_field(name="指令前綴", value="/", inline=False)
            await channel.send(embed=embed)
    except Exception as e:
        # 印出錯誤原因
        for BOT_SEND_CHENNEL_ID in BOT_SEND_CHENNELS_ID:
            channel = discord.utils.get(bot.get_all_channels(), id=int(BOT_SEND_CHENNEL_ID))
            embed = discord.Embed(title="「神鷹教・對 bug 特別作戰部隊」總部公告", description="緊急狀況! 通訊系統受到攻擊，出現異常!", color=0x00EC00)
            embed.add_field(name="Error: ", value=sys.exc_info()[0], inline=False)
            await channel.send(embed=embed)

    Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式
    Time_Check_cf.start()

@bot.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == bot.user:
        return
    elif "Sys call" in message.content:
        await message.channel.send("現在改用斜線指令瞜，請用 `/` 作為指令前綴!")


if __name__ == "__main__":
    try:
        with open("env.json") as f:
            envDict = json.load(f)
            BOT_SEND_CHENNELS_ID = envDict["BOT_SEND_CHENNELS_ID"]
            DISCORD_BOT_APIKEY = envDict["DISCORD_BOT_APIKEY"]
            if(len(BOT_SEND_CHENNELS_ID)==0 or DISCORD_BOT_APIKEY==""):
                print("env.json 設定錯誤，請依照 Readme 指示填入")
                sys.exit(1)
    except FileNotFoundError:
        print("env.json檔案不存在, 請在與 Discord_Bot.py 的相同資料夾下建立 env.json 檔案，並依照 Readme 指示填入")
        sys.exit(1)
    
    bot.run(DISCORD_BOT_APIKEY) #啟動bot
