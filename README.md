# Binance Futures Testnet Trading Bot

Small Python CLI application for placing `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M). The code is structured into separate validation, client/API, business logic, and CLI layers with file-based logging and clear error handling.

## Features

- Place `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports both `BUY` and `SELL`
- Validates CLI input before sending any API request
- Logs API requests, responses, and failures to a rotating log file
- Clean, reusable structure suitable for an interview submission

## Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── cli.py
│   ├── client.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── logs/
│   └── .gitkeep
├── .env.example
├── README.md
└── requirements.txt
```

## Setup

1. Create and activate a Python 3 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Binance Futures Testnet API credentials:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

4. Make sure your Binance Testnet account is funded with test USDT and that the symbol you trade is enabled on USDT-M Futures.

## How to Run

### Market Order

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### Limit Order

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 90000
```

### Validation Examples

Missing price for limit order:

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --order-type LIMIT --quantity 0.001
```

Unexpected price for market order:

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001 --price 90000
```

## Output

The CLI prints:

- Order request summary
- Order response details including `orderId`, `status`, `executedQty`, and `avgPrice` when available
- Clear success or failure messages

## Logging

- Log file path: `logs/trading_bot.log`
- Logged events include:
  - API request metadata
  - API response payloads
  - API errors
  - Network failures

For the application task submission, place one market order and one limit order, then include the generated log file(s) from `logs/`.

## Assumptions

- Credentials are provided through environment variables in `.env`
- Only USDT-M Futures Testnet is targeted
- `LIMIT` orders are sent with `timeInForce=GTC`
- `newOrderRespType=RESULT` is used to make the response more useful from the CLI

## Notes

- Binance may reject orders that violate symbol filters such as minimum quantity, quantity step size, or price tick size.
- If that happens, the application will surface the Binance API error and the full response will be written to the log file.

## Submission Checklist

- Source code
- `README.md`
- `requirements.txt`
- One successful `MARKET` order log
- One successful `LIMIT` order log

