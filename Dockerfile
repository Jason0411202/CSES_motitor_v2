# 使用 Python 官方镜像作为基础
FROM python:3.11.3-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装所需的依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 容器启动命令
CMD [ "python", "Discord_Bot.py" ]
