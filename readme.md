# 指令
```bash
sudo docker build -t "cses_monitor_v2" .
sudo docker run --restart=always -d cses_monitor_v2
```

# 環境變數
在專案資料夾根目錄新增 env.json，內容範例如下
```bash
{
    "BOT_SEND_CHENNELS_ID": [107581537815617817, 10754182351785321],
    "DISCORD_BOT_APIKEY": "MTIgasuidgfuiwbfiuqwbfiuoewshbfoiwehfoewhfogiwefhpiwegh"
}
```
