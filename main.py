import logging
import os
import asyncio
from datetime import datetime
from decimal import Decimal
from tinkoff.invest import MoneyValue
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
import matplotlib.pyplot as plt  # Импортируем библиотеку для построения графиков

TOKEN = 't.l8Mdl_lwveoIDsCr1yzueG0OVyBcjVqlsXukD6W8Vj3006R5v-VF1pYwOmQIm37n5Xa_1pZRE2u4OZjULRLRkQ'
if TOKEN is None:
    raise ValueError("Environment variable INVEST_TOKEN is not set. Please set it before running the script.")

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Списки для хранения времени и цен для двух акций
time_data = []
price_data_stock1 = []  # Для первой акции
price_data_stock2 = []  # Для второй акции

def add_money_sandbox(client, account_id, money, currency="rub"):
    """Function to add money to sandbox account."""
    money = decimal_to_quotation(Decimal(money))
    return client.sandbox.sandbox_pay_in(
        account_id=account_id,
        amount=MoneyValue(units=money.units, nano=money.nano, currency=currency),
    )     

async def print_prices(client):
    """Функция для периодического получения и вывода цен акций."""
    global time_data, price_data_stock1, price_data_stock2  # Используем глобальные списки для хранения данных
    while True:
        try:
            prices = client.market_data.get_last_prices(figi=['BBG004730N88', 'BBG004730ZJ9'])
            print(f"\nЦены на {datetime.now()}")
            for price in prices.last_prices:
                price_decimal = quotation_to_decimal(price.price)
                print(f"FIGI: {price.figi}, Цена: {price_decimal}")
                
                # Сохраняем данные для построения графика
                time_data.append(datetime.now())
                if price.figi == 'BBG004730N88':
                    price_data_stock1.append(price_decimal)  # Для первой акции
                elif price.figi == 'BBG004730ZJ9':
                    price_data_stock2.append(price_decimal)  # Для второй акции

                # Построение графика
                plt.clf()  # Очищаем предыдущий график
                plt.plot(time_data, price_data_stock1, label='Акция 1 (BBG004730N88)', color='blue')
                plt.plot(time_data, price_data_stock2, label='Акция 2 (BBG004730ZJ9)', color='orange')
                plt.xlabel('Время')
                plt.ylabel('Цена')
                plt.title('Изменение цен акций во времени')
                plt.legend()
                plt.xticks(rotation=45)  # Поворачиваем метки по оси X для удобства
                plt.pause(0.1)  # Пауза для обновления графика

        except Exception as e:
            logger.error(f"Ошибка при получении цен: {e}")
        
        await asyncio.sleep(10)  # пауза 10 секунд

async def main():
    """Example - How to set/get balance for sandbox account.
    How to get/close all sandbox accounts.
    How to open new sandbox account."""
    with SandboxClient(TOKEN) as client:
        # get all sandbox accounts
        sandbox_accounts = client.users.get_accounts()
        print(sandbox_accounts)
        
        # Запуск бесконечного цикла получения цен
        await asyncio.wait_for(print_prices(client), timeout=600)

if __name__ == "__main__":
    plt.ion()  # Включаем интерактивный режим для matplotlib
    asyncio.run(main())
