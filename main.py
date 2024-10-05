import aiohttp
import asyncio
import json
import time
import sys
import uuid
import os
import colorama

version= 'Version 2.3'
error_count = 0
succes_count = 0
userName = None

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
        return f"{response * 1000:.2f}"
    return 'ping Failed'

def centered(text) -> str:
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

def task() -> str:
    if config['setting']['paid']:
        return 'Waiting For Paid'
    return 'Waiting For Web'

async def auth_check() -> None:
    global userName
    async with aiohttp.ClientSession() as session:
        async with session.get('https://users.roblox.com/v1/users/authenticated',
                               cookies={'.ROBLOSECURITY': config['roblox']['cookies']}, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                print('Cookies Are Valid. Continuing.')
                if config['setting']['privacy']['name']:
                    userName = data['name']
                else:
                    userName = 'Anonymous'
            else:
                print('Cookies aren\'t valid. Please recheck them.')
                sys.exit()

            if config['webhook']['enable']:
                async with aiohttp.ClientSession() as hook:
                    async with hook.post(config['webhook']['url'], json={
                        "embeds": [{
                            "description": "Webhooks Now will wait for request.",
                            "color": 3066993
                        }]
                    }) as res:
                        if res.ok:
                            print('Webhook Working. Continuing.')

asyncio.run(auth_check())

async def thumbnail_url(asset) -> str:
    async with aiohttp.ClientSession() as thumb:
        async with thumb.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={asset}&returnPolicy=PlaceHolder&size=75x75&format=Png&isCircular=false") as photo:
            if photo.status == 200:
                url = await photo.json()
                return url['data'][0]['imageUrl']
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
                                print(response)

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

async def get_serial(type, asset) -> str:
    async with aiohttp.ClientSession() as tag:
        async with tag.get(f'https://inventory.roblox.com/v2/users/{await get_userid()}/inventory/{type}?limit=10&sortOrder=Desc', 
        cookies={'.ROBLOSECURITY': config['roblox']['cookies']}, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                for item in data['data']:
                    if item['assetId'] == asset:
                        return item['serialNumber']
            return 'N/A'

async def get_name(asset) -> str:
    global datas
    async with aiohttp.ClientSession() as name:
        async with name.get(f'https://economy.roblox.com/v2/developer-products/{asset}/info', ssl=False) as response:
            if response.status == 200:
                datas = await response.json()
                return datas['Name']
            return str(asset)

async def economy(asset) -> dict:
    global response, payload, error_count
    async with aiohttp.ClientSession() as economyInfo:
        async with economyInfo.get(f'https://economy.roblox.com/v2/assets/{asset}/details', ssl=False) as data:
            if data.status == 200:
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
                if config['webhook']['url'] and config['webhook']['message']['error']:
                    await webhook(await get_name(asset), '**Failed**\n\nCannot buy the item due to lack of detail.\n\nReason: ``Rate limit economy API``', 8388608, asset)
                return {}


async def buy_item() -> None:
    global error_count, succes_count, last_bought
    async with aiohttp.ClientSession() as buy:
        async with buy.post(
            f'https://apis.roblox.com/marketplace-sales/v1/item/{response["CollectibleItemId"]}/purchase-item',
            headers={'x-csrf-token': await get_xcsrf()},
            cookies={'.ROBLOSECURITY': config['roblox']['cookies']},
            json=payload, 
            ssl=False
        ) as bought:
            buy_response = await bought.json()

            if buy_response.get('purchased', False):
                last_bought = response['Name']
                succes_count += 1
                append_succes(response['Name'])
                if config['webhook']['url'] and config['webhook']['message']['succes']:
                    await webhook(
                        response['Name'],
                        f'**Successfully Bought Serial** #``{await get_serial(response["AssetTypeId"], response["AssetId"])}``',
                        16761021,
                        response['AssetId']
                    )
            elif bought.status == 429:
                error_message = await bought.text()
                print(error_message)
                append_error('Ratelimit', 'buy_item Function')
                error_count += 1
                if config['webhook']['url'] and config['webhook']['message']['error']:
                    await webhook(response['Name'], '``Ratelimit Retrying.``', 8388608, response['AssetId'])
            else:
                error_message = await bought.text()
                print(error_message)
                error_count += 1
                append_error(error_message, 'Buy_item function')
                if config['webhook']['url'] and config['webhook']['message']['error']:
                    await webhook(response['Name'], error_message, 8388608, response['AssetId'])                    
                        

async def theme() -> None:
    while True:
        console_clear()
        tag = """
███╗   ██╗███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
████╗  ██║██╔════╝██╔══██╗██║██║   ██║████╗ ████║
██╔██╗ ██║█████╗  ██████╔╝██║██║   ██║██╔████╔██║
██║╚██╗██║██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
██║ ╚████║███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
                                                 
"""
        design = f"""
{Style.BRIGHT}╭──────────────────────────╮{Style.RESET_ALL}
{Fore.MAGENTA}        INFORMATION     {Style.RESET_ALL}
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}
{Fore.CYAN}    User: {Fore.YELLOW}{userName}{Style.RESET_ALL}        
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}
{Fore.CYAN} Latency: {Fore.YELLOW}{latency()} ms{Style.RESET_ALL}  
{Fore.CYAN}            Task: {Fore.YELLOW}{task()}{Style.RESET_ALL}       
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}
{Fore.GREEN} Last Bought:  {Fore.WHITE}{last_bought}{Style.RESET_ALL}
{Fore.GREEN} Last Detected: {Fore.WHITE}{last_detected}{Style.RESET_ALL}
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}
{Fore.RED} Errors:      {Fore.WHITE}{error_count}{Style.RESET_ALL} 
{Fore.GREEN} Successes:   {Fore.WHITE}{succes_count}{Style.RESET_ALL}
{Style.BRIGHT}╰──────────────────────────╯{Style.RESET_ALL}
{Style.BRIGHT}╭──────────────────────────╮{Style.RESET_ALL}
{Fore.MAGENTA}        VERSION        {Style.RESET_ALL}
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}
{Fore.CYAN}       {Fore.YELLOW}{version}{Style.RESET_ALL}       
{Style.BRIGHT}╰──────────────────────────╯{Style.RESET_ALL}
"""
        centered(Style.BRIGHT + tag)
        centered(design)
        await asyncio.sleep(1)

async def main() -> None:
    global bar, last_detected
    bar = None
    asyncio.create_task(theme())
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get("https://pastefy.app/Pq7EfNmH/raw", ssl=False) as paste:
                    try:
                        qux = json.loads(await paste.text())
                    except json.JSONDecodeError:
                        continue

                    quux = qux['Paid']['id'] if config['setting']['paid'] else qux['Web']['id']

                    if bar is not None and quux != bar:
                        print(quux)
                        last_detected = await get_name(quux)

                        if config['setting']['paid']:
                            await economy(quux)
                            if response['PriceInRobux'] in config['setting']['price']:
                                for _ in range(config['setting']['limit']):
                                    await buy_item()
                        else:
                            await economy(quux)
                            if response['PriceInRobux'] == 0:
                                for _ in range(4):
                                    bought = await buy_item()
                                    if bought.status == 429:
                                        for _ in range(4):
                                            await buy_item()
                            else:
                                append_error('Prices', 'Price doesn\'t match')
                                if config['webhook']['url'] and config['webhook']['message']['error']:
                                    await webhook(await get_name(quux), 'Price Doesn\'t match, continue watching.', 8388608, int(quux))

                    bar = quux

            except asyncio.TimeoutError:
                continue

if __name__ == "__main__":
    asyncio.run(main())
