# sese bot
[English README](./README_EN.md)


## 获取 Token
1. 创建 Telegram Bot  
根据[官方文档](https://core.telegram.org/bots#3-how-do-i-create-a-bot)创建 Telegram 机器人，获得机器人的 token
2. 获取 Pixiv refresh token  
使用 [`gppt`](https://github.com/eggplants/get-pixivpy-token) 获取 Pixiv refresh token


## 部署 
### 使用 Docker (推荐)  
1. 下载 `config` 和 `docker-compose.yml`，文件结构如下：
```
sesebot/
    config/
        config.json
        token.json
    docker-compose.yml
```
2. 在 `token.json` 中填入 pixiv token 和 telegrame bot token
3. 在 `sesebot` 中执行 `docker compose up -d`  
   (支持 `x64` 和 `arm64`，如果你的CPU架构是 `arm64`，需要将 `docker-compose.yml` 中的 `amd64` tag 改为 `arm64`)

### 使用 Python3.10
1. 克隆本项目
2. `pip install -r requirements.txt`  
3. 安装 [`Redis`](https://github.com/redis/redis)
1. 在 `token.json` 中填入 pixiv token 和 telegrame bot token
2. 在 `config.json` 填入 redis 的地址和端口
3. `python src/main.py`