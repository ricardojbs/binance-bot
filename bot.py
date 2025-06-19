from keep_alive import keep_alive
keep_alive()  # Inicia o servidor Flask

import time
from binance.client import Client

# 🔑 Chaves da API diretamente no código (somente para testes!)
API_KEY = '845de591b6e72842bbc6ec55453478354d1695c1d704875e26db007aa3f0fb0f'
API_SECRET = 'f5381dc75c32c9cea0854793710c18b1dca9c3be01ee1620440ef9383dd7bd1c'

# Inicializa Binance Testnet
client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

symbol = 'BTCUSDT'
quantity = 0.001

def get_price():
    ticker = client.futures_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def has_open_position():
    positions = client.futures_account()['positions']
    for p in positions:
        if p['symbol'] == symbol and float(p['positionAmt']) != 0:
            return True
    return False

def buy():
    if has_open_position():
        print("⛔ Já existe uma posição aberta. Ignorando BUY.")
        return
    print("🟢 Comprando")
    return client.futures_create_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quantity=quantity
    )

def sell():
    if has_open_position():
        print("⛔ Já existe uma posição aberta. Ignorando SELL.")
        return
    print("🔴 Vendendo")
    return client.futures_create_order(
        symbol=symbol,
        side='SELL',
        type='MARKET',
        quantity=quantity
    )

def get_last_candle():
    candles = client.futures_klines(symbol=symbol, interval='1m', limit=1)
    return float(candles[0][1]), float(candles[0][4])  # open, close

def simple_bot():
    last_candle_time = None

    while True:
        candles = client.futures_klines(symbol=symbol, interval='1m', limit=1)
        candle = candles[0]
        open_price = float(candle[1])
        close_price = float(candle[4])
        candle_close_time = candle[6]  # timestamp de fechamento do candle

        if last_candle_time is None or candle_close_time > last_candle_time:
            print(f"\n🕒 Novo candle fechado!")
            print(f"Open: {open_price:.2f} | Close: {close_price:.2f}")

            if has_open_position():
                print("⏳ Posição já aberta — aguardando reversão.")
            else:
                if close_price > open_price:
                    print("📈 Candle de alta — ENTRADA LONG")
                    buy()
                elif close_price < open_price:
                    print("📉 Candle de baixa — ENTRADA SHORT")
                    sell()
                else:
                    print("😐 Candle neutro — sem ação.")

            last_candle_time = candle_close_time

        else:
            print(".", end="", flush=True)  # só esperando o próximo candle

        time.sleep(3)


if __name__ == '__main__':
    simple_bot()
