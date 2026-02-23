# LLMCryptocurrency


LLMCryptocurrency 是一个基于 Python 的轻量级加密货币量化分析与交易脚本示例，使用多时间框架（4h/1h/15m）获取行情、计算技术指标（RSI、MACD、MA、ATR 等），并将数据发送至 LLM（DeepSeek）以生成交易决策。脚本同时包含与区块链交互的函数（使用 web3.py）用于批准、买入与卖出代币。

## 主要功能

- 从交易所（使用 ccxt，示例为 Binance）抓取多时间框架 K 线数据。
- 计算常见技术指标：RSI、MACD、MA20、ATR 等。
- 使用 DeepSeek（调用 OpenAI 风格接口）生成基于多时间框架的交易建议（严格 JSON 返回）。
- 支持通过 web3.py 在链上签名并提交交易（approve、swap 等）。

## 重要警告（请务必阅读）

- 本仓库不包含任何私钥或 API key。所有敏感信息均通过环境变量读取（例如 `.env`）。
- 绝对不要将含有私钥或凭证的文件（如 `.env`）加入到 Git 仓库或公开托管平台。
- 在将任何交易功能用于主网之前，务必在测试网充分测试。
- 对真实资金操作请保持谨慎，并确保代码经过安全审计。

## 环境与依赖

建议使用虚拟环境（venv 或 conda）。主要依赖：

- Python 3.10+
- ccxt
- pandas
- openai / deepseek SDK（示例中使用 `OpenAI` 客户端）
- python-dotenv
- web3
- requests

示例安装：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

（如果工程中未包含 `requirements.txt`，可手动安装：`pip install ccxt pandas python-dotenv web3 requests openai`）

## 必要的环境变量

脚本通过 `os.getenv` 获取下列变量（请在本地用 `.env` 或环境变量管理工具注入）：

- RPC_URL
- WALLET_ADDRESS
- WALLET_PRIVATE_KEY
- ALCHEMY_API_KEY
- chain_ID
- QuickSwap_Router_Address
- usdt_address（示例中的 stablecoin 地址）
- wpol_address（示例中的代币地址）
- DEEPSEEK_API_KEY
- symbol（如 "POL/USDT"）
- Blockchain_node_access_address

示例 `.env.template`（不要把真实密钥上传）：

```
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

## 使用方法（快速开始）

1. 配置虚拟环境并安装依赖。
2. 在项目根创建 `.env` 并填入真实凭证（仅在本地使用）。
3. 先在非生产环境或测试网运行脚本，确认逻辑与签名无误：

```bash
python LLMCryptocurrency.py
```

脚本会周期性（示例为每 450 秒）运行主循环，调用 LLM 获取交易建议并根据 JSON 决策执行相应操作（买入/卖出/观望）。
