# 指令
```bash
sudo docker build -t "cses_monitor_v2" .
sudo docker run --restart=always --env-file .env -d cses_monitor_v2
```

或者
```bash
docker compose up -d
```

# 環境變數
```bash
# .env
# 這個檔案是用來設定環境變數的
BOT_SEND_CHENNEL_ID=
DISCORD_BOT_APIKEY=
```
