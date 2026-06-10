# LLMCryptocurrency

LLMCryptocurrency 是一个基于 Python 的加密货币量化分析与自动交易脚本。它从交易所获取多时间框架行情数据，计算技术指标，并调用 DeepSeek（LLM）生成交易决策，最终通过 web3.py 在链上执行买入、卖出或观望操作。

## 功能

- 从交易所（示例中为 Binance）抓取 4h、1h、15m 的 K 线数据
- 计算 RSI、MACD、MA20、ATR 等常用技术指标
- 将多时间框架数据与当前持仓发送至 DeepSeek API，获得结构化的交易建议（JSON 格式）
- 支持通过 QuickSwap 路由器在 Polygon 网络上执行代币交换
- 自动批准稳定币授权（Approve）
- 周期性运行（默认每 450 秒），实现循环决策

## 技术栈

- Python 3.10+
- [ccxt](https://github.com/ccxt/ccxt) – 交易所行情数据
- [pandas](https://pandas.pydata.org/) – 数据处理
- [web3.py](https://web3py.readthedocs.io/) – 区块链交互
- [python-dotenv](https://github.com/theskumar/python-dotenv) – 环境变量加载
- [OpenAI Python SDK](https://github.com/openai/openai-python) – 调用 DeepSeek API
- [requests](https://docs.python-requests.org/) – HTTP 请求（Alchemy 接口）

## 项目结构

```
.
├── .env                     # 环境变量（请勿提交到 Git）
├── LLMCryptocurrency.py     # 主脚本
├── README.md                # 本文件
```

## 环境要求

- Python 3.10 或更高版本
- 一个可用的 Polygon (MATIC) 钱包，并持有少量 MATIC 作为 Gas 费
- DeepSeek API Key（或其他兼容 OpenAI 接口的 LLM 服务）
- Binance API 访问权限（用于获取行情，无需交易权限）
- Alchemy 或 Infura 节点访问地址

## 安装

1. 克隆仓库：

```bash
git clone <repository-url>
cd LLMCryptocurrency
```

2. 创建并激活虚拟环境（推荐）：

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

如果项目中没有 `requirements.txt`，可以手动安装：

```bash
pip install ccxt pandas python-dotenv web3 requests openai
```

## 配置

在项目根目录创建 `.env` 文件，填入以下变量（示例值请替换为真实信息）：

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

**安全警告**：`.env` 文件包含私钥和 API 密钥，请勿将其加入版本控制。建议将 `.env` 添加到 `.gitignore` 中。

## 使用方法

在配置好 `.env` 后，直接运行脚本：

```bash
python LLMCryptocurrency.py
```

脚本会执行以下流程：

1. 连接区块链节点，检查连接状态
2. 从 Binance 获取 4h、1h、15m 的 OHLCV 数据
3. 计算技术指标（RSI、MACD、MA20、ATR）
4. 组合当前持仓比例（基于钱包代币和稳定币价值）
5. 生成提示并调用 DeepSeek API
6. 解析 LLM 返回的 JSON 决策：
   - **买入**：将稳定币兑换为代币（先授权，后交换）
   - **卖出**：将代币兑换为稳定币
   - **观望**：不执行任何操作
7. 暂停 450 秒后重新开始循环

按 `Ctrl+C` 可安全退出循环。

## 脚本说明

| 函数 / 模块 | 功能 |
|------------|------|
| `get_tokenbalance()` | 获取钱包原生代币（如 POL）余额（wei） |
| `get_stablecoinbalance()` | 通过 Alchemy API 查询稳定币（如 USDT）余额 |
| `get_price()` | 从 Binance 获取交易对当前价格 |
| `fetch_multi_timeframe_data()` | 获取多个时间框架的 K 线数据 |
| `calculate_indicators()` | 计算 RSI、MACD、MA20、ATR |
| `generate_ai_prompt()` | 构造发送给 LLM 的提示（含市场数据与规则） |
| `ask_deepseek()` | 调用 DeepSeek API 并返回 JSON 响应 |
| `swap_token_to_stablecoin()` | 通过 QuickSwap 将代币兑换为稳定币 |
| `swap_stablecoin_to_token()` | 通过 QuickSwap 将稳定币兑换为代币 |
| `approve_stablecoin()` | 授权路由器使用稳定币 |

## 注意事项

- 本脚本默认使用 **Polygon 主网**（chain_ID = 137）。请确认路由器地址、代币地址与网络匹配。
- 交易前请先在 **测试网** 充分验证逻辑，避免因代码错误导致资金损失。
- DeepSeek 模型返回的决策仅供参考，不构成投资建议。
- 脚本使用了代理（127.0.0.1:7890）以访问外网，若无需代理可注释相应代码。
- 主循环每 450 秒执行一次，可自行调整 `time.sleep(450)` 的值。

## 贡献

欢迎提交 Issue 或 Pull Request。在贡献前请确保：

- 代码风格与现有脚本一致
- 添加必要的注释
- 不要在代码中硬编码敏感信息
- 在测试环境验证修改

## 许可证

此项目中未找到许可证文件。请在使用前联系作者获取许可或根据默认版权法律处理。