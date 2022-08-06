# sese bot


# Deploy  
## Environment
`pip install -r requirements.txt`  

## Config
1. Create Telegram Bot
Create your Telegram bot cccording to [Official Docs](https://core.telegram.org/bots#3-how-do-i-create-a-bot), and get the token of your telegram bot.

2. Get Pixiv refresh token  
Obtain Pixiv refresh token using [`gppt`](https://github.com/eggplants/get-pixivpy-token).

3. Install Redis  
Install [`Redis`](https://github.com/redis/redis)

4. Configure `sese boot`  
Rename `config.json.example` to `config.json`. Edit it if you need.  
Rename `token.json.example` to `token.json` and then place your telegram bot token and pixiv refresh token at `pixiv`, `bot` 

## Run   
1. Start bot: `python src/bot.py`
2. Start grabbing from pixiv: `python src/grab.py`
3. Start pushing: `python src/push.py`