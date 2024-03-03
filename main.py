import sys
import asyncio
from aiohttp import ClientSession, ClientError
from datetime import datetime, timedelta


async def fetch_exchange_rate(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date.strftime('%d.%m.%Y')}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                eur_rate = next((item for item in data['exchangeRate'] if item.get('currency') == 'EUR'), None)
                usd_rate = next((item for item in data['exchangeRate'] if item.get('currency') == 'USD'), None)
                return {
                    date.strftime('%d.%m.%Y'): {
                        'EUR': {'sale': eur_rate.get('saleRate'), 'purchase': eur_rate.get('purchaseRate')},
                        'USD': {'sale': usd_rate.get('saleRate'), 'purchase': usd_rate.get('purchaseRate')}
                    }
                }
            else:
                return {date.strftime('%d.%m.%Y'): 'Error fetching data'}
    except ClientError as e:
        return {date.strftime('%d.%m.%Y'): str(e)}


async def main(days):
    if days > 10 or days < 1:
        print("Please enter a number of days between 1 and 10.")
        return

    async with ClientSession() as session:
        tasks = [fetch_exchange_rate(session, datetime.now() - timedelta(days=day)) for day in range(days)]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result)


if __name__ == "__main__":
    try:
        days = int(sys.argv[1]) # number of days you want to list
        asyncio.run(main(days))
    except IndexError:
        print("Usage: python main.py <number_of_days>")
    except ValueError:
        print("Please provide the number of days as an integer.")
