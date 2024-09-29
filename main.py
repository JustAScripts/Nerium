import aiohttp
import asyncio
import json
import time
import sys
import uuid
import os
import colorama

error_count = 0
succes_count = 0

last_bought = None
last_detected = None

from datetime import datetime
from ping3 import ping
from colorama import Fore, Style

with open('config.json', 'r') as files:
    config = json.load(files)

def console_clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def latency() -> float:
    response = ping('google.com')
    if response is not None:
        return f"{response * 1000:.2f} ms"
    else:
        return 'ping Failed'

def centered(text):
    console_width = os.get_terminal_size().columns
    for line in text.strip().split("\n"):
        print(line.center(console_width))

def append_succes(name) -> None:
    with open('succes.txt', 'a') as sc:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sc.write(f'{time}\n-> Successfully Bought {name}\n\n')

def append_error(text, source) -> None:
    with open('error.txt', 'a') as er:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        er.write(f'{time}\nerror -> {text}\nsource -> {source}\n\n')

async def auth_check() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://users.roblox.com/v1/users/authenticated',
                               cookies={'.ROBLOSECURITY': config['roblox']['cookies']}, ssl=False) as response:
            if response.status == 200:
                print('Cookies Are Valid. Continuing.')
            else:
                print('Cookies aren\'t valid. Please recheck them.')
                sys.exit()
            
            if config['webhook']['enable']:
                async with aiohttp.ClientSession() as hook:
                    async with hook.post(config['webhook']['url'], json={
                        "embeds": [{
                            "description": "*Successfully set up*\n\n*This webhook will notify when an error occurs or successful purchases happen",
                            "color": 3066993
                        }]
                    }) as res:
                        if res.ok:
                            print('Webhook Working. Continuing.')
                        else:
                            a = await res.text()
                            print(a)

asyncio.run(auth_check())

async def thumbnail_url(asset) -> str:
    async with aiohttp.ClientSession() as thumb:
        async with thumb.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={asset}&returnPolicy=PlaceHolder&size=75x75&format=Png&isCircular=false") as photo:
            if photo.status == 200:
                url = await photo.json()
                return url['data'][0]['imageUrl']
            else:
                return 'https://cdn.discordapp.com/attachments/1287218202111246336/1289710777200152647/Picsart_24-09-22_14-27-23-475.png?ex=66f9d042&is=66f87ec2&hm=c9c55840dd6df5cb363a668795ea67607f59228bc0a56c538812de71f620ddeb&'

async def webhook(title: str, description: str, color: int, asset: str) -> None:
    async with aiohttp.ClientSession() as dis:
        async with dis.post(config['webhook']['url'],
                            json={
                                "embeds": [{
                                    "title": str(title),
                                    "url": f'https://www.roblox.com/catalog/{asset}',
                                    "description": str(description),
                                    "footer": {
                                        "text": "Flower Sniper V2"
                                    },
                                    "color": int(color),
                                    "thumbnail": {
                                        "url": await thumbnail_url(asset)
                                    }
                                }]
                            }) as response:
            print(await response.text())

async def get_xcsrf() -> str:
    async with aiohttp.ClientSession() as token:
        async with token.post('https://auth.roblox.com/v2/logout',
        cookies={'.ROBLOSECURITY': config['roblox']['cookies']}, ssl=False) as response:
            if response.ok:
                return await response.text()
            else:
                return response.headers.get("x-csrf-token")

async def get_userid() -> int:
    async with aiohttp.ClientSession() as id:
        async with id.get('https://users.roblox.com/v1/users/authenticated',
        cookies={'.ROBLOSECURITY': config['roblox']['cookies']}, ssl=False) as response:
            if response.ok:
                fetch_id = await response.json()
                return fetch_id.get('id')

async def economy(asset) -> dict:
    async with aiohttp.ClientSession() as economyInfo:
        async with economyInfo.get(f'https://economy.roblox.com/v2/assets/{asset}/details', ssl=False) as data:
            if data.status == 200:
                global response, payload, error_count
                response = await data.json()
                payload = {
                    "collectibleItemId": str(response['CollectibleItemId']),
                    "collectibleProductId": str(response['CollectibleProductId']),
                    "expectedCurrency": 1,
                    "expectedPrice": str(response['PriceInRobux']),
                    "idempotencyKey": str(uuid.uuid4()),
                    "expectedSellerId": str(response['Creator']['Id']),
                    "expectedSellerType": str(response['Creator']['CreatorType']),
                    "expectedPurchaserType": "User",
                    "expectedPurchaserId": await get_userid()
                }
                return payload
            elif data.status == 429:
                tc = await data.text()
                error_count += 1
                append_error(tc, 'Economy Api Ratelimit')

async def buy_item() -> None:
    global error_count, succes_count, last_bought
    async with aiohttp.ClientSession() as buy:
        async with buy.post(f'https://apis.roblox.com/marketplace-sales/v1/item/{response["CollectibleItemId"]}/purchase-item',
        headers={'x-csrf-token': await get_xcsrf()},
        cookies={'.ROBLOSECURITY': config['roblox']['cookies']},
            json=payload) as bought:
                buy_it_fuck = await bought.json()
                if buy_it_fuck['purchased']:
                    res = await bought.text()
                    last_bought = response['Name']
                    succes_count += 1
                    append_succes(response['Name'])
                    if config['webhook']['url']:
                        await webhook(response['Name'], 'Successfully Bought', 16761021, response['AssetId'])
                elif bought.status == 429:
                    print(await bought.text())
                    append_error('Ratelimit', 'buy_item Function')
                    error_count += 1
                    if config['webhook']['url']:
                        await webhook(response['Name'], '``Ratelimit Retrying.``', 8388608, response['AssetId'])
                else:
                    print(await bought.text())
                    error_count += 1
                    append_error(await bought.text(), 'Buy_item function')
                    if config['webhook']['url']:
                        await webhook(response['Name'], await bought.text(), 8388608, response['AssetId'])

def theme():
    console_clear()
    tag = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣴⡦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡟⣳⣿⣰⢄⠀⠀⠀⣠⣤⣤⣶⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣉⠷⠿⣾⠁⠀⣼⣿⣿⣿⣿⣿⡃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣷⣄⠹⣷⡀⣿⡿⠋⣹⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣷⣦⡀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⣿⣿⣿⣿⣆⠀⣠⣤⣀⠀⠀⠀⠀⣴⣿⣿⣿⣿⠉⢻⣧⢿⣷⢿⠃⣴⡿⢟⣋⣁⡀⠀⠀⠀⠀⠀⢀⡀⢸⣿⣿⣿⣿⡇⣴⣿⣿⣶⣤
⠀⢠⣦⣜⢿⣿⣟⢻⣿⣾⣿⣿⣿⣿⡆⠀⠀⠈⣩⣽⣿⣛⣻⣦⡙⢸⣿⡇⢸⡵⠾⢿⣿⣿⣿⡇⠀⠀⠀⠀⠘⢿⣲⣿⣿⣧⢹⣿⡿⣿⣿⣿⣿
⠀⢀⣭⣭⣽⣿⣿⣼⡿⠛⣹⣿⣿⠿⠁⠀⠀⠸⣿⣿⣿⣿⠉⠉⢁⠈⠉⠁⣩⣤⣀⡘⠻⣿⣿⣿⣿⣦⠀⠀⣾⣿⣿⠿⢿⣻⣿⡏⠰⣿⣛⡋⠁
⢀⣾⣿⣿⣉⣭⣷⠛⣻⣄⢻⣷⣦⣄⠀⠀⠀⣴⣿⣿⣿⣿⣀⣴⣫⣶⠂⠀⠻⢿⣽⣿⣿⣿⣿⣿⡿⠏⠀⠸⣿⣿⣿⣿⣿⣿⣰⣿⣷⣽⣿⣿⣷
⠈⠻⢿⣿⠟⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⢿⣿⣿⣿⣿⡿⣱⣿⣧⣠⡄⠰⣾⣿⣿⣯⠻⠿⠟⠁⠀⠀⠀⠈⠙⠋⢸⣿⣿⣿⣿⠹⣿⣿⣿⠿
⠀⠀⠀⠀⠸⣿⣿⣿⣿⡇⠻⠿⠟⠋⠀⠀⠀⠀⠈⠙⠛⠋⠀⣿⣿⣿⣿⣷⣴⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⡿⠀⠈⠉⠀⠀
⠀⠀⠀⠀⠀⠻⠿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠿⠿⢿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""
    design = f"""        
┌────── ⋆⋅☆⋅⋆ ──────┐


 INFORMATION

 Latency 
 {latency()}

 Runtime 
      


 ──────────────────

   
  Last Bought 
 {last_bought}

  Last Detected
 {last_detected}


 ──────────────────

  
  Error 
{error_count}

  Success 
{succes_count}


└────── ⋆⋅☆⋅⋆ ──────┘



"""
    centered(Fore.MAGENTA + Style.BRIGHT + tag)
    centered(Fore.GREEN + Style.BRIGHT + design)

async def main() -> None:
     global bar, last_detected
     bar = None
     async with aiohttp.ClientSession() as session:
        while True:
            async with session.get("https://pastefy.app/Pq7EfNmH/raw") as paste:
                qux = json.loads(await paste.text())
                quux = qux['Paid']['id'] if config['setting']['paid'] else qux['Web']['id']

                if bar is not None and quux != bar:
                    if 2 > 1:
                        print(quux)
                        await economy(quux)
                        last_detected = quux
                        if config['setting']['paid']:
                            if response['PriceInRobux'] in config['setting']['price']:
                                for _ in range(1, 1 + config['setting']['limit']):
                                     await buy_item()
                        else:
                            if response['PriceInRobux'] == 0:
                                for _ in range(1, 5):
                                     print(response['Name'])
                bar = quux

            theme()
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
