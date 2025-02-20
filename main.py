import os
import time
from tinkoff.invest import Client, OrderDirection, OrderType
from tinkoff.invest.services import SandboxService
from tinkoff.invest.utils import quotation_to_decimal
from tinkoff.invest.constants import INVEST_GRPC_API_SANDBOX

# Set your Tinkoff Invest Sandbox API token and account ID
TINKOFF_SANDBOX_API_TOKEN = os.getenv("TINKOFF_SANDBOX_API_TOKEN", "t.fRiYtbf1zp3RiEeeztP59KBL4GWSZojqB8-2ndtu6CcRX9A9frdBbdRZMKJxD6wqSsjM7ECjc3b3cQNpkeQB1g")
SANDBOX_ACCOUNT_ID = os.getenv("TINKOFF_SANDBOX_ACCOUNT_ID", "")

# Define the instrument to trade (e.g., SBER for Sberbank shares)
INSTRUMENT_TICKER = "SBER"
INSTRUMENT_FIGI = "BBG004730N88"  # Replace with the actual FIGI of the instrument

# Trading parameters
TRADE_AMOUNT = 1  # Number of shares to trade
BUY_THRESHOLD = 250.0  # Buy if price drops below this threshold
SELL_THRESHOLD = 260.0  # Sell if price rises above this threshold

def get_last_price(client, figi):
    """Fetch the last price of the instrument."""
    response = client.market_data.get_last_prices(figi=[figi])
    return float(quotation_to_decimal(response.last_prices[0].price))

def place_order(client, account_id, figi, direction, quantity, price):
    """Place an order on the market."""
    order_response = client.orders.post_order(
        figi=figi,
        quantity=quantity,
        price=quotation_to_decimal(price),
        direction=direction,
        account_id=account_id,
        order_type=OrderType.ORDER_TYPE_LIMIT,
    )
    return order_response

def trading_strategy(client, account_id, figi):
    """Simple trading strategy: Buy if price drops below threshold, sell if price rises above threshold."""
    last_price = get_last_price(client, figi)
    print(f"Last price of {INSTRUMENT_TICKER}: {last_price}")

    # Buy if price drops below the buy threshold
    if last_price < BUY_THRESHOLD:
        print(f"Price dropped below {BUY_THRESHOLD}! Buying {TRADE_AMOUNT} shares of {INSTRUMENT_TICKER}...")
        place_order(client, account_id, figi, OrderDirection.ORDER_DIRECTION_BUY, TRADE_AMOUNT, last_price)

    # Sell if price rises above the sell threshold
    elif last_price > SELL_THRESHOLD:
        print(f"Price rose above {SELL_THRESHOLD}! Selling {TRADE_AMOUNT} shares of {INSTRUMENT_TICKER}...")
        place_order(client, account_id, figi, OrderDirection.ORDER_DIRECTION_SELL, TRADE_AMOUNT, last_price)

def main():
    with Client(TINKOFF_SANDBOX_API_TOKEN, target=INVEST_GRPC_API_SANDBOX) as client:
        print("Connected to Tinkoff Invest Sandbox API")

        # Ensure the sandbox account has funds
        sandbox_service = SandboxService(client,[])
        sandbox_service.sandbox_pay_in(account_id=SANDBOX_ACCOUNT_ID, amount=quotation_to_decimal(100000))

        while True:
            try:
                trading_strategy(client, SANDBOX_ACCOUNT_ID, INSTRUMENT_FIGI)
                time.sleep(60)  # Wait for 1 minute before checking again
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()
