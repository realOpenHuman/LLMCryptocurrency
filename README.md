```markdown
# LLMCryptocurrency

An automated cryptocurrency trading bot that combines multi-timeframe technical analysis with a large language model (DeepSeek) to execute on-chain swaps on Polygon via QuickSwap.

## Overview

LLMCryptocurrency is a Python script that continuously monitors a Binance trading pair (e.g., POL/USDT) and uses a DeepSeek-powered AI to decide whether to buy, sell, or hold. It pulls OHLCV data across three timeframes, calculates common indicators (RSI, MACD, MA20, ATR), and builds a structured prompt that includes your current on-chain position ratio. The LLM returns a JSON decision, and the bot automatically executes the appropriate swap through QuickSwap smart contracts, handling token approvals and slippage automatically.

This project is experimental and intended for developers interested in AI-driven DeFi automation, not as financial advice or a production-ready trading system.

## Features

- Multi-timeframe market data from Binance (4h, 1h, 15m) via ccxt
- Technical indicators: RSI, MACD (DIF, DEA, histogram), MA20, ATR
- Integration with DeepSeek (OpenAI‑compatible API) for trading decisions
- On‑chain swaps using QuickSwap router on Polygon:
  - `swapExactTokensForETH` (sell native token)
  - `swapExactETHForTokens` (buy native token)
- Automatic ERC‑20 stablecoin approval before a swap
- Position‑aware logic – the AI knows your current portfolio split
- Configurable loop interval and all parameters via `.env`

## Tech Stack

- **Python 3.10+**
- **ccxt** – unified exchange API for market data
- **pandas** – data manipulation and indicator calculation
- **web3.py** – Ethereum/Polygon blockchain interaction
- **python-dotenv** – environment variable loading
- **OpenAI Python SDK** – LLM API client (used with DeepSeek base URL)
- **requests** – Alchemy token balance API

## Project Structure

```
.
├── .env                     # Environment variables (create from template)
├── LLMCryptocurrency.py     # Main trading bot script
├── LICENSE                  # MIT License
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- A Polygon (MATIC) wallet with a small amount of MATIC for gas
- DeepSeek API key (or another OpenAI-compatible endpoint)
- Access to a Polygon Mainnet node (Alchemy, Infura, or similar)
- Stablecoin and wrapped token contract addresses for the assets you plan to trade

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
   There is no `requirements.txt` at the moment; the command above installs everything needed.

### Configuration

Copy the provided `.env` template and fill in your own values:

```env
RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY
WALLET_ADDRESS=0xYourAddress
WALLET_PRIVATE_KEY=PUT_PRIVATE_KEY_HERE
ALCHEMY_API_KEY=your_alchemy_key
chain_ID=137
QuickSwap_Router_Address=0x...    # QuickSwap router on Polygon
usdt_address=0x...                # Stablecoin contract (e.g., USDT or USDC)
wpol_address=0x...                # Wrapped native token (e.g., WPOL or WETH)
DEEPSEEK_API_KEY=your_deepseek_key
symbol=POL/USDT                   # Binance trading pair
Blockchain_node_access_address=https://polygon-mainnet.g.alchemy.com/v2/your_key
```

| Variable                            | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| `RPC_URL`                           | Polygon Mainnet JSON-RPC endpoint (Infura, Alchemy, etc.)                   |
| `WALLET_ADDRESS`                    | Your personal wallet address (checksummed)                                  |
| `WALLET_PRIVATE_KEY`                | Private key for signing transactions – **keep this secret**                  |
| `ALCHEMY_API_KEY`                   | Used for token balance queries (Alchemy endpoint)                           |
| `chain_ID`                          | Chain ID (137 for Polygon Mainnet)                                           |
| `QuickSwap_Router_Address`          | QuickSwap router contract address on Polygon                                |
| `usdt_address`                      | Stablecoin contract address (e.g., USDT)                                    |
| `wpol_address`                      | Wrapped native token address (e.g., WPOL)                                   |
| `DEEPSEEK_API_KEY`                  | DeepSeek API key                                                             |
| `symbol`                            | Binance trading pair, e.g., `POL/USDT`                                      |
| `Blockchain_node_access_address`    | Alchemy endpoint for token balance lookups                                  |

> **Never commit your `.env` file.** Add it to `.gitignore` immediately.

### Running the Bot

Start the bot with:

```bash
python LLMCryptocurrency.py
```

On launch the script will:

1. Verify connectivity to the Polygon node.
2. Fetch 4h, 1h, 15m OHLCV data from Binance.
3. Compute technical indicators.
4. Retrieve your current on-chain position (native token vs. stablecoin).
5. Build a prompt and send it to DeepSeek.
6. Parse the JSON response and execute a **buy**, **sell**, or **hold**.
7. Wait 450 seconds and repeat.

Press `Ctrl+C` to stop the loop gracefully.

## Usage

### Decision Flow

The bot calculates your current portfolio split between the native token (e.g., WPOL) and the stablecoin (e.g., USDT) and includes that percentage in the prompt. The AI must return a strict JSON response, for example:

```json
{
    "交易货币": "POL/USDT",
    "趋势方向": "上涨",
    "交易决策": "买入",
    "持仓百分比": "60%",
    "核心理由": "4h uptrend confirmed by 1h and 15m signals"
}
```

Based on the `交易决策` field:

- **买入 (Buy)**: The required amount of stablecoin is swapped to the native token via `swapExactTokensForETH`.
- **卖出 (Sell)**: The required amount of native token is swapped to stablecoin via `swapExactETHForTokens`.
- **观望 (Hold)**: No transaction; the bot waits for the next cycle.

Only the difference between your current position and the target is traded, and a 5% slippage tolerance is applied.

### Important Notes

- **Test on a testnet first.** The code may contain bugs or lead to loss of funds. Use only risk capital.
- The script includes a hard‑coded local HTTP proxy (`127.0.0.1:7890`). If you do not use a proxy, **remove or comment out** the relevant lines in `LLMCryptocurrency.py`.
- Double‑check all contract addresses in `.env` are correct on Polygon Mainnet.
- The loop interval (`time.sleep(450)`) can be adjusted in the source code.
- DeepSeek outputs are generated by an AI model and **do not constitute financial advice**.

## Roadmap

No formal roadmap is defined. The repository appears to be a proof‑of‑concept. Possible enhancements include:

- Support for additional DEX routers or networks
- Dynamic proxy configuration from environment variables
- Robust error handling and logging
- Unit tests and CI integration

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository and create a feature branch.
2. Set up a development environment using the steps above.
3. Make your changes and test thoroughly on a testnet.
4. Open a pull request with a clear description of what you changed.

Please ensure that any sensitive credentials are never committed, and follow Python best practices.

## License

This project is licensed under the [MIT License](LICENSE).

```
© (c) 2026 OpenHuman
```