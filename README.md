# sese bot
[English README](./README_EN.md)

# 部署  
## 环境
`pip install -r requirements.txt`  
## 配置
1. 创建 Telegram Bot
根据[官方文档](https://core.telegram.org/bots#3-how-do-i-create-a-bot)创建 Telegram 机器人，获得机器人的Token

2. 获取 Pixiv refresh token  
使用 [`gppt`](https://github.com/eggplants/get-pixivpy-token) 获取 Pixiv refresh token

3. 安装 Redis  
安装并配置 [`Redis`](https://github.com/redis/redis)

4. 配置 `sese boot`  
重命名 `config.json.example` 为 `config.json`, 根据需要修改内容  
重命名 `token.json.example` 为 `token.json`, 分别在 `pixiv`, `bot` 填入 telegram bot token 和 pixiv refresh token

## 启动  
`python src/main.py`