# sese bot

## Get Token
1. Create Telegram Bot  
Create Telegram bot and get the token according to [Officials Manual](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
2. Get Pixiv refresh token  
Use [`gppt`](https://github.com/eggplants/get-pixivpy-token) to get Pixiv refresh token


## Deploy  
### Use Docker (Recommended)  
1. Download `config` folder and `docker-compose.yml` with file structure as below:
```
sesebot/
    config/
        config.json
        token.json
    docker-compose.yml
```
2. Fill your pixiv token and telegrame bot token into `token.json`
3. In `sesebot` folder, execute `docker compose up -d`
(only support `x64` and `arm64` architecture, if your device's arch is `arm64`, please modify the image tag in `docker-compose.yml` to `arm64`)

### Use raw Python3.10
1. Clone this repository
2. `pip install -r requirements.txt`  
3. Install [`Redis`](https://github.com/redis/redis)
2. Fill your pixiv token and telegrame bot token into `token.json`
3. Fill host and port of your redis server into `config.json`
4. `python src/main.py`