# LLMCryptocurrency

A Python-based automated cryptocurrency trading script that combines multi-timeframe technical analysis with a large language model (DeepSeek) to generate on-chain trading decisions on Polygon via QuickSwap.

## Overview

LLMCryptocurrency fetches market data from Binance, calculates common technical indicators (RSI, MACD, MA20, ATR), and sends a structured prompt to a DeepSeek model. The model returns a JSON decision (Buy/Sell/Hold) along with a suggested position allocation. The script then interacts with QuickSwap smart contracts on Polygon to execute the trade, after handling token approvals if necessary. The process runs in a continuous loop, by default every 450 seconds.

## Features

- Multi-timeframe OHLCV data collection (4h, 1h, 15m) from Binance via ccxt
- Calculation of RSI, MACD, MA20, and ATR indicators
- Integration with DeepSeek API for trading decisions (JSON output)
- On-chain execution of swaps through QuickSwap router contracts (swap exact tokens for ETH / swap exact ETH for tokens)
- Automatic approval of stablecoins for the router
- Periodic decision loop with configurable interval

## Tech Stack

- Python 3.10+
- [ccxt](https://github.com/ccxt/ccxt) – Exchange data fetching
- [pandas](https://pandas.pydata.org/) – Data handling and indicators
- [web3.py](https://web3py.readthedocs.io/) – Blockchain interactions on Polygon
- [python-dotenv](https://github.com/theskumar/python-dotenv) – Environment variable loading
- [OpenAI Python SDK](https://github.com/openai/openai-python) – Used to call DeepSeek API
- [requests](https://docs.python-requests.org/) – HTTP calls (Alchemy token balance API)

## Project Structure

```
.
├── .env                     # Environment variables (do not commit)
├── LLMCryptocurrency.py     # Main trading script
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A Polygon (MATIC) wallet with a small amount of MATIC for gas
- DeepSeek API key (or another OpenAI-compatible LLM service)
- Access to Binance market data (public endpoints; no trading permissions needed)
- An Alchemy or Infura node endpoint for Polygon Mainnet

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd LLMCryptocurrency
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install required packages:
   ```bash
   pip install ccxt pandas python-dotenv web3 requests openai
   ```
   If a `requirements.txt` is present, use `pip install -r requirements.txt`.

### Configuration

Copy the provided `.env` template and fill in your real values:

```env
RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY
WALLET_ADDRESS=0xYourAddress
WALLET_PRIVATE_KEY=PUT_PRIVATE_KEY_HERE
ALCHEMY_API_KEY=your_alchemy_key
chain_ID=137
QuickSwap_Router_Address=0x...
usdt_address=0x...
wpol_address=0x...
DEEPSEEK_API_KEY=your_deepseek_key
symbol=POL/USDT
Blockchain_node_access_address=https://polygon-mainnet.g.alchemy.com/v2/your_key
```

- `RPC_URL` / `Blockchain_node_access_address` – Polygon node endpoints (Infura / Alchemy).
- `QuickSwap_Router_Address` – QuickSwap router contract address on Polygon.
- `usdt_address` – Stablecoin token address (e.g., USDT).
- `wpol_address` – Wrapped native token address (e.g., WETH, WPOL).
- `symbol` – Trading pair on Binance (POL/USDT).

> **Security:** Never commit the `.env` file. Add it to `.gitignore`.

### Running the Project

With environment configured, start the bot:

```bash
python LLMCryptocurrency.py
```

The script will:

1. Check blockchain node connectivity.
2. Fetch multi-timeframe OHLCV data.
3. Compute technical indicators.
4. Calculate current position ratio (token vs. stablecoin value).
5. Construct a prompt and send it to DeepSeek.
6. Parse the JSON response and execute a trade (buy / sell) or hold.
7. Sleep for 450 seconds, then repeat.

Press `Ctrl+C` to stop.

## Usage

### How It Works

The bot detects the current on-chain balances of your native token (e.g., WPOL) and stablecoin (USDT), then derives the current position percentage. It combines this with multi-timeframe market data and sends a prompt that instructs the LLM to return a JSON like:

```json
{
    "交易货币": "POL/USDT",
    "趋势方向": "上涨",
    "交易决策": "买入",
    "持仓百分比": "60%",
    "核心理由": "4h trend up, 1h and 15m confirm"
}
```

Depending on the decision:

- **Buy**: swaps stablecoins → native token via `swapExactTokensForETH`
- **Sell**: swaps native token → stablecoins via `swapExactETHForTokens`
- **Hold**: no action

### Key Functions

| Function | Description |
|----------|-------------|
| `get_tokenbalance()` | Native token balance (wei) |
| `get_stablecoinbalance()` | Stablecoin balance via Alchemy API |
| `get_price()` | Current price from Binance |
| `fetch_multi_timeframe_data()` | Downloads 4h, 1h, 15m OHLCV data |
| `calculate_indicators()` | Computes RSI, MACD, MA20, ATR |
| `generate_ai_prompt()` | Builds the LLM prompt with market data and rules |
| `ask_deepseek()` | Calls DeepSeek API and returns JSON string |
| `swap_token_to_stablecoin()` | Executes sell order on QuickSwap |
| `swap_stablecoin_to_token()` | Executes buy order on QuickSwap |
| `approve_stablecoin()` | Approves router to spend stablecoin |

## Important Notes

- The bot is designed for **Polygon Mainnet** (chain ID 137). Verify all contract addresses used.
- **Test thoroughly on testnet** before using real funds. The script may contain bugs that could lead to loss.
- DeepSeek (or any LLM) responses are for informational purposes and do **not** constitute financial advice.
- The code includes a local proxy (`127.0.0.1:7890`). If you do not use a proxy, remove or comment those lines.
- The main loop interval (`time.sleep(450)`) can be adjusted in the source.
- Stablecoin and native token addresses are expected in the `.env`; make sure they match the asset you intend to trade.

## License

License information was not found in this repository. Please contact the author for usage terms.