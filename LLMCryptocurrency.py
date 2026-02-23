import ccxt
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from web3 import Web3
import time
from decimal import Decimal, getcontext
import json
import requests
import logging


getcontext().prec = 18
load_dotenv()
os.environ['HTTP_PROXY'] = ""
os.environ['HTTPS_PROXY'] = ""
os.environ['http_proxy'] = ""
os.environ['https_proxy'] = ""
logger = logging.getLogger(__name__)
RPC_URL = os.getenv("RPC_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
WALLET_ADDRESS = Web3.to_checksum_address(WALLET_ADDRESS)
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
chain_ID = os.getenv("chain_ID")
w3= Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
session = requests.Session()
session.trust_env = False
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890' 
}
session.proxies.update(proxies)
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
QuickSwap_Router_Address = os.getenv("QuickSwap_Router_Address")
Stablecoin_address = os.getenv("usdt_address")     # Load your stablecoin's address such as USDT or USDC
Token_address = os.getenv("wpol_address")   # Load your token's address such as POL or ETH
exchange = ccxt.binance(
    {
        'urls': {
        'api': {
            'dapiPublic': 'https://dapi1.binance.com/dapi/v1',
            'dapiPrivate': 'https://dapi1.binance.com/dapi/v1',
        }
    },
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    },
    'options': {
        'adjustForTimeDifference': True, 
    },
}
    )
symbol=os.getenv("symbol")
Blockchain_node_access_address = os.getenv("Blockchain_node_access_address")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
router_abi = json.loads('''
[
    {"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"}
]
''')

time.sleep(3)
if not w3.is_connected():
    print("连接失败")
    exit()

router_abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view", 
        "type": "function"
        },
    {
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "amountOutMin", "type": "uint256"},
        {"name": "path", "type": "address[]"},
        {"name": "to", "type": "address"},
        {"name": "deadline", "type": "uint256"}
    ],
    "name": "swapExactTokensForETH",
    "outputs": [{"name": "amounts", "type": "uint256[]"}],
    "stateMutability": "nonpayable",
    "type": "function"
}
]

erc20_abi = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]




def get_tokenbalance() -> Decimal:
    balance = w3.eth.get_balance(WALLET_ADDRESS)
    balance = Decimal(str(balance))
    return balance # amount as wei

def get_stablecoinbalance(wallet_address,Stablecoin_address,url) -> Decimal:  # the url is a blockchain node access address
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [
            wallet_address,
            [Stablecoin_address]
        ]
    }
    response = session.post(url, json=payload, timeout=10)
    result = response.json()
    token_balance_hex = result['result']['tokenBalances'][0]['tokenBalance']
    balance = Decimal(int(token_balance_hex, 16)).scaleb(-6)
    return balance  # amount as USDT/USDC

def get_price() -> Decimal: #amount as USDT/USDC
    try:
        ticker = exchange.fetch_ticker(symbol)
        last = ticker.get('last')
        if last is None:
            raise ValueError(f"fetch_ticker returned no last price for {symbol}: {ticker}")
        price = Decimal(str(last))
        return price
    except Exception as e:
        logger.error(f"Fail to get price from Binance: {e}")
        raise Exception("Unable to get price")


def swap_token_to_stablecoin(token:int):# wei
    router_contract = w3.eth.contract(address=QuickSwap_Router_Address, abi=router_abi)
    deadline = int(time.time()) + 600
    less_amount_out = int((Decimal(token).scaleb(-18)*get_price()) * Decimal('0.95'))
    transaction = router_contract.functions.swapExactETHForTokens(less_amount_out,
[Token_address, Stablecoin_address],
WALLET_ADDRESS,
deadline).build_transaction({
'from': WALLET_ADDRESS,
'value': token,
'gas': 250000,
'gasPrice': w3.eth.gas_price,
'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
'chainId': int(chain_ID) # check on https://chainlist.org/
})
    signed_tx = w3.eth.account.sign_transaction(transaction, WALLET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"The transaction has been completed , hash: {w3.to_hex(tx_hash)}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status == 1:
        print("done")
    else:
        print("Reverted")
    return tx_hash

def approve_stablecoin(amount:Decimal):# USDT/USDC
    stablecoin_contract = w3.eth.contract(address=Stablecoin_address, abi=erc20_abi)
    
    current_allowance = stablecoin_contract.functions.allowance(WALLET_ADDRESS, QuickSwap_Router_Address).call()
    if current_allowance >= amount:
        print("已有足够授权，跳过 Approve")
        return True

    print(f"正在授权 USDT 给 QuickSwap...")
    tx = stablecoin_contract.functions.approve(QuickSwap_Router_Address, amount).build_transaction({
        'from': WALLET_ADDRESS,
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 137
    })
    signed_tx = w3.eth.account.sign_transaction(tx, WALLET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Successfully approved")

def swap_stablecoin_to_token(amount):  # USDT/USDC
    amount = int(Decimal(amount).scaleb(6))
    approve_stablecoin(amount)
    router_contract = w3.eth.contract(address=QuickSwap_Router_Address, abi=router_abi)
    deadline = int(time.time()) + 600
    path = [Stablecoin_address, Token_address]
    min_pol_out = int(router_contract.functions.getAmountsOut(amount, path).call()[-1] * 0.95)
    transaction = router_contract.functions.swapExactTokensForETH(
        amount,
        min_pol_out,
        path,
        WALLET_ADDRESS,
        deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
        'gas': 250000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 137
    })

    signed_tx = w3.eth.account.sign_transaction(transaction, WALLET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"The sell order has been submitted:{w3.to_hex(tx_hash)}")
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def fetch_multi_timeframe_data(symbol):
    timeframes = {'4h': 100, '1h': 100, '15m': 100}
    data = {}
    for tf, limit in timeframes.items():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = calculate_indicators(df)
            data[tf] = df
        except Exception as e:
            logger.error(f"unable to get {tf}:{e}")
            raise
    return data

def calculate_indicators(df):
    period = 14
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp1 - exp2
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = 2 * (df['DIF'] - df['DEA'])

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['ATR'] = calculate_atr(df)
    return df

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def generate_ai_prompt(data, symbol):
    tf_4h = data['4h'].iloc[-1]
    tf_1h = data['1h'].iloc[-1]
    tf_15m = data['15m'].iloc[-1]
    volatility_15m = ((tf_15m['high'] - tf_15m['low']) / tf_15m['close'] * 100)
    global position
    position = get_tokenbalance().scaleb(-18)*get_price()/(get_stablecoinbalance(WALLET_ADDRESS,Stablecoin_address,Blockchain_node_access_address)+get_tokenbalance().scaleb(-18)*get_price())
    # print(get_tokenbalance().scaleb(-18))
    # print(get_price())
    # print(get_stablecoinbalance(WALLET_ADDRESS,Stablecoin_address,Blockchain_node_access_address))
    prompt = f"""分析资产: {symbol}

【趋势判断 - 4小时线】
价格: {tf_4h['close']:.4f}, RSI: {tf_4h['RSI']:.2f}, MACD: {tf_4h['MACD_Hist']:.4f}, MA20: {tf_4h['MA20']:.4f}

【交易信号 - 1小时线】
价格: {tf_1h['close']:.4f}, RSI: {tf_1h['RSI']:.2f}, MACD: {tf_1h['MACD_Hist']:.4f}, MA20: {tf_1h['MA20']:.4f}

【入场时机 - 15分钟线】
价格: {tf_15m['close']:.4f}, RSI: {tf_15m['RSI']:.2f}, 波动: {volatility_15m:.2f}%, ATR: {tf_15m['ATR']:.4f}

当前持仓：{str(position*100)[:4]+"%"}

任务：基于多时间框架分析给出决策。
- 4h判断主要趋势方向（上涨/下跌/震荡）
- 1h和15m信号需同向确认买入、卖出机会

约束：
1. 仅当4h趋势向上且1h/15m信号也看涨时，才考虑买入。
2. 若震荡，则观望。
3. 若1h和15m趋势都看跌，则卖出
4. 给出你建议的持仓百分比，如果是观望，则将持仓百分比定为当前持仓百分比
请严格按以下JSON格式返回，不含任何其他文字：
{{
    "交易货币": "{symbol}",
    "趋势方向": "上涨/震荡/下跌",
    "交易决策": "买入/观望/卖出",
    "持仓百分比": "5%~100%"
    "核心理由": "简要分析"
}}"""
    return prompt


def ask_deepseek(prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner", 
            messages=[
                {"role": "system", "content": "你是一名专业的加密货币量化交易员，擅长通过技术指标给出冷静的交易指令，必须严格按 JSON 格式返回，不得包含任何解释性文字。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用 API 出错: {e}"

def main():
    data = fetch_multi_timeframe_data(symbol)
    prompt = generate_ai_prompt(data, symbol)
    print(prompt)
    LLMresponse = ask_deepseek(prompt) # return str
    print(LLMresponse)
    LLMresponse = json.loads(LLMresponse)
    if LLMresponse["交易决策"] == "观望":
        print("Watching and waiting")
        return
    elif LLMresponse["交易决策"] == "买入":
        delta_position=Decimal(LLMresponse["持仓百分比"][:-1]).scaleb(-2)-position
        if delta_position<=0:
            logger.error("Error position from LLM")
            return
        else:
            token =delta_position*(get_stablecoinbalance(WALLET_ADDRESS,Stablecoin_address,Blockchain_node_access_address)+get_tokenbalance().scaleb(-18)*get_price())
            stablecoin = token*get_price()
            print(f"buy in {stablecoin:4f} "+symbol.split("/")[1])
            swap_stablecoin_to_token(stablecoin)
    elif LLMresponse["交易决策"] == "卖出":
        delta_position= position-Decimal(LLMresponse["持仓百分比"][:-1]).scaleb(-2)
        if delta_position<=0:
            logger.error("Error position from LLM")
            return
        else:
            stablecoin = delta_position*(get_stablecoinbalance(WALLET_ADDRESS,Stablecoin_address,Blockchain_node_access_address)+get_tokenbalance().scaleb(-18)*get_price())
            token = int((stablecoin/get_price()).scaleb(18))
            print(f"sold out {stablecoin/get_price():4f}"+symbol.split("/")[0])
            swap_token_to_stablecoin(token)

if __name__=="__main__":
    while True:
        try:
            main()
            time.sleep(450)
        except KeyboardInterrupt:
            break
        except Exception:
            continue
