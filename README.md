# LLMCryptocurrency

An automated cryptocurrency trading bot that uses multi-timeframe technical analysis and a large language model (DeepSeek) to make on-chain trading decisions on Polygon via QuickSwap.

## Overview

LLMCryptocurrency fetches OHLCV market data from Binance, computes common technical indicators (RSI, MACD, MA20, ATR), and sends a structured prompt to a DeepSeek model. The model returns a JSON trading decision (Buy, Sell, or Hold) together with a suggested position allocation. Based on that decision the script executes token swaps through QuickSwap smart contracts on the Polygon network, handling token approvals automatically. The process runs continuously in a loop, re-evaluating the market at a configurable interval.

## Features

- Multi-timeframe data collection (4h, 1h, 15m) from Binance via ccxt
- Calculation of RSI, MACD, MA20, and ATR indicators
- Integration with DeepSeek (OpenAI-compatible) API for trading decisions in strict JSON format
- On-chain buy and sell execution using QuickSwap router contracts (`swapExactTokensForETH` / `swapExactETHForTokens`)
- Automatic ERC-20 stablecoin approval before a swap
- Position-aware decision engine – the LLM sees the current on-chain position ratio
- Configurable loop interval and environment via `.env` file

## Tech Stack

- Python 3.10+
- [ccxt](https://github.com/ccxt/ccxt) – exchange data API
- [pandas](https://pandas.pydata.org/) – technical indicator computation
- [web3.py](https://web3py.readthedocs.io/) – Polygon blockchain interaction
- [python-dotenv](https://github.com/theskumar/python-dotenv) – environment variable management
- [OpenAI Python SDK](https://github.com/openai/openai-python) – LLM API client (used with DeepSeek base URL)
- [requests](https://docs.python-requests.org/) – Alchemy token balance API

## Project Structure

```
.
├── .env                     # Configuration file (create from template)
├── LLMCryptocurrency.py     # Main trading script
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- A Polygon (MATIC) wallet funded with a small amount of MATIC for gas
- A DeepSeek API key (or another OpenAI-compatible endpoint)
- Public Binance market data (no trading permissions required)
- Access to a Polygon Mainnet node (Alchemy or Infura)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd LLMCryptocurrency
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/macOS
   .venv\Scripts\activate         # Windows
   ```

3. Install the required packages:
   ```bash
   pip install ccxt pandas python-dotenv web3 requests openai
   ```
   If a `requirements.txt` is present, use `pip install -r requirements.txt` instead.

### Configuration

Create a `.env` file in the project root with the following variables (refer to the provided `.env` template):

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

**Configuration items explained**

| Variable | Description |
|----------|-------------|
| `RPC_URL` | Polygon mainnet JSON-RPC endpoint (Infura or similar) |
| `WALLET_ADDRESS` | Your personal wallet address (checksummed) |
| `WALLET_PRIVATE_KEY` | Private key for signing transactions – **keep secret** |
| `ALCHEMY_API_KEY` | (Optional) Used for token balance queries via Alchemy |
| `chain_ID` | Chain ID (137 for Polygon Mainnet) |
| `QuickSwap_Router_Address` | QuickSwap router contract address on Polygon |
| `usdt_address` | Stablecoin contract address (e.g., USDT) |
| `wpol_address` | Wrapped native token address (e.g., WPOL, WETH) |
| `DEEPSEEK_API_KEY` | API key for DeepSeek |
| `symbol` | Binance trading pair (e.g., `POL/USDT`) |
| `Blockchain_node_access_address` | Alchemy endpoint for token balance lookups |

> **Security:** Never commit your `.env` file. Add it to `.gitignore` immediately.

### Running the Project

Start the bot with:

```bash
python LLMCryptocurrency.py
```

The script will:

1. Verify connectivity to the Polygon node.
2. Fetch 4h, 1h, 15m OHLCV data from Binance.
3. Compute technical indicators.
4. Determine the current on-chain position ratio (native token vs. stablecoin).
5. Build a decision prompt and send it to the DeepSeek API.
6. Parse the JSON response and execute a buy, sell, or hold action.
7. Wait for 450 seconds and repeat.

Press `Ctrl+C` to stop the loop gracefully.

## Usage

### Decision Flow

The bot determines your current portfolio split between the native token (e.g., WPOL) and the stablecoin (e.g., USDT) and includes that information in the prompt. The LLM is instructed to return a JSON object like:

```json
{
    "交易货币": "POL/USDT",
    "趋势方向": "上涨",
    "交易决策": "买入",
    "持仓百分比": "60%",
    "核心理由": "4h trend up, 1h and 15m confirm"
}
```

Based on the `交易决策` field:

- **买入 (Buy)** – the amount of stablecoin needed to reach the target position is swapped to the native token via `swapExactTokensForETH`.
- **卖出 (Sell)** – the amount of native token to reduce the position is swapped to the stablecoin via `swapExactETHForTokens`.
- **观望 (Hold)** – the bot waits for the next cycle without executing any transaction.

Only the difference between the current position and the suggested target is traded, and a 5% slippage tolerance is built into the swap transactions.

### Important Notes

- The script is built for **Polygon Mainnet** (chain ID 137). Double-check all contract addresses before running.
- **Test on a testnet first.** The code may contain bugs; use risk capital you can afford to lose.
- DeepSeek responses are generated by an AI model and do **not** constitute financial advice.
- The code includes a hard‑coded local proxy (`127.0.0.1:7890`). If you do not use a proxy, remove or comment those lines in `LLMCryptocurrency.py`.
- The loop interval (`time.sleep(450)`) can be changed directly in the source.
- Token and router addresses in `.env` must match the assets you intend to trade.

## License

License information was not found in this repository. Please contact the author for usage terms.