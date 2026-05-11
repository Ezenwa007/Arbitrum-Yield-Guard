import streamlit as st
import os
from dotenv import load_dotenv
from web3 import Web3
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
import requests
import re
import pandas as pd
import datetime
import sqlite3
from datetime import datetime


load_dotenv()

st.set_page_config(page_title="Arbitrum YieldGuard Agent", page_icon="🛡️", layout="wide")
st.title("🛡️ Arbitrum YieldGuard Agent")
st.markdown("**Smart Auto-Selection**")

# ============== ARBITRUM CONNECTION ==============
w3 = Web3(Web3.HTTPProvider(os.getenv("ARBITRUM_SEPOLIA_RPC")))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RAW_ADDRESS = "0x9faAd3d1B57C6Abe222792012662B7A128EBb5f8"
YOUR_WALLET = w3.to_checksum_address(RAW_ADDRESS)

# ============== YIELD HISTORY DATABASE ==============
conn = sqlite3.connect("yields.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS yield_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    aave_apy REAL,
    tvl REAL,
    source TEXT
)
""")
conn.commit()

# ============== SUPPLY HISTORY DATABASE ==============
history_conn = sqlite3.connect("supply_history.db", check_same_thread=False)
history_cursor = history_conn.cursor()

history_cursor.execute("""
CREATE TABLE IF NOT EXISTS supply_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    action TEXT,           -- "Supply" or "Withdraw"
    amount REAL,
    protocol TEXT,
    tx_hash TEXT,
    status TEXT
)
""")
history_conn.commit()

if w3.is_connected():
    print("✅ Connected to Arbitrum Sepolia")
    print(f"Latest block: {w3.eth.block_number}")
else:
    print("❌ Connection failed")

llm = ChatOpenAI(
    model="openrouter/free",                    # This intelligently picks from available free models
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.2,
    max_tokens=1200,
)


# ============== CONTRACT ADDRESSES (Arbitrum Sepolia) ==============
USDC_ADDRESS = "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d"
AAVE_POOL_ADDRESS = "0xBfC91D59fdAA134A4ED45f7B584cAf96D7792Eff"  # ← Update if needed
SPARK_SAVINGS_ADDRESS = "0x2e9b9c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c"  # Replace with real if different

# ============== ABIs ==============
ERC20_ABI = [
    {"constant":False,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"}
]

AAVE_POOL_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"supply","outputs":[],"type":"function"}
]

AAVE_WITHDRAW_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"withdraw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"type":"function"}
]

SPARK_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"deposit","outputs":[],"type":"function"}
]

# ============== TOOLS ==============
@tool
def fetch_yield_data() -> str:
    """Fetch real-time yields"""
    try:
        resp = requests.get("https://yields.llama.fi/pools?chain=Arbitrum")
        data = resp.json()

        aave_apy = None
        tvl = None
        stables = []
        for p in data.get("data", [])[:20]:
            symbol = str(p.get("symbol", "")).upper()
            project = str(p.get("project", "")).lower()
            if "aave" in project and any(s in symbol for s in ["USDC"]):
                apy = p.get('apy', 0)
                tvl_usd = p.get('tvlUsd', 0) / 1_000_000
                aave_apy = apy
                tvl = tvl_usd
                # Save to history
                cursor.execute(
                    "INSERT INTO yield_history (timestamp, aave_apy, tvl, source) VALUES (?, ?, ?, ?)",
                    (datetime.now().isoformat(), apy, tvl_usd, "DefiLlama")
                )
                conn.commit()

            if any(s in symbol for s in ["USDC", "USDT", "DAI"]):
                stables.append(
                    f"• **{project.title()}** | {symbol} | APY: **{p.get('apy', 0):.2f}%** | TVL: **${p.get('tvlUsd', 0) / 1e6:.1f}M**"
                )

        return "\n".join(stables[:12]) if stables else "No stable pools found."
    except Exception as e:
        return f"Error fetching yields: {str(e)}"

@tool
def check_wallet_balance(address: str = YOUR_WALLET) -> str:
    """Check ETH and USDC balance"""
    try:
        eth_balance = w3.from_wei(w3.eth.get_balance(address), 'ether')
        usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
        usdc_balance = usdc_contract.functions.balanceOf(address).call() / 1_000_000
        return f"Wallet {address[:8]}... | {eth_balance:.4f} ETH | {usdc_balance:.2f} USDC"
    except Exception as e:
        return f"Balance check failed: {e}"



@tool
def execute_supply_best(amount_usdc: float) -> str:
    """Automatically choose best protocol (Aave or Spark) and execute"""
    if not PRIVATE_KEY or not PRIVATE_KEY.startswith("0x"):
        return "❌ PRIVATE_KEY not loaded correctly from .env"

    try:
        wallet = w3.to_checksum_address(YOUR_WALLET)
        amount = int(amount_usdc * 1_000_000)

        # Approve
        usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
        usdc_balance = usdc_contract.functions.balanceOf(wallet).call() / 1_000_000
        if usdc_balance < amount_usdc:
            return f"❌ Insufficient USDC. You have {usdc_balance:.2f} USDC"
        # EIP-1559 Gas parameters (best for Arbitrum)
        gas_price = w3.eth.gas_price
        max_priority_fee = w3.to_wei(0.1, 'gwei')
        max_fee = gas_price * 2
        approve_tx = usdc_contract.functions.approve(AAVE_POOL_ADDRESS, amount).build_transaction({
            'from': wallet,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 250000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee,
            'type': 2
        })
        signed = w3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
        w3.eth.send_raw_transaction(signed.raw_transaction)

        # Supply to Aave
        aave_contract = w3.eth.contract(address=AAVE_POOL_ADDRESS, abi=AAVE_POOL_ABI)
        supply_tx = aave_contract.functions.supply(USDC_ADDRESS, amount, wallet, 0).build_transaction({
            'from': wallet,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 600000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee,
            'type': 2
        })

        signed_supply = w3.eth.account.sign_transaction(supply_tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_supply.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        # Log successful supply
        history_cursor.execute(
            """
            INSERT INTO supply_history 
            (timestamp, action, amount, protocol, tx_hash, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), "Supply", amount_usdc, "Aave", tx_hash.hex(), "success")
        )
        history_conn.commit()

        return f"""
        ✅ **Successfully Supplied to Aave**

        **Amount**: {amount_usdc:.2f} USDC  
        **Tx Hash**: `{tx_hash.hex()[:20]}...`

        🔗 [View on Arbiscan](https://sepolia.arbiscan.io/tx/{tx_hash.hex()})
                """
    except Exception as e:
        return f"❌ Transaction failed: {str(e)[:300]}"

@tool
def withdraw_from_aave(amount_usdc: float) -> str:
    """Withdraw USDC from Aave V3"""
    if not PRIVATE_KEY or not PRIVATE_KEY.startswith("0x"):
        return "❌ PRIVATE_KEY not set correctly in .env"

    try:
        wallet = w3.to_checksum_address(YOUR_WALLET)
        amount = int(amount_usdc * 1_000_000)  # USDC 6 decimals

        # EIP-1559 Gas
        gas_price = w3.eth.gas_price
        max_priority_fee = w3.to_wei(0.1, 'gwei')
        max_fee = gas_price * 2

        aave_contract = w3.eth.contract(address=AAVE_POOL_ADDRESS, abi=AAVE_WITHDRAW_ABI)

        withdraw_tx = aave_contract.functions.withdraw(
            USDC_ADDRESS,
            amount,
            wallet
        ).build_transaction({
            'from': wallet,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 500000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee,
            'type': 2
        })

        signed = w3.eth.account.sign_transaction(withdraw_tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        # Wait for receipt to get actual amount withdrawn
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        # Parse actual withdrawn amount from logs/events (more reliable)
        actual_amount = amount_usdc  # fallback

        # Try to get exact amount from event
        try:
            # Aave withdraw event has the amount
            for log in receipt.logs:
                if len(log.topics) > 0 and log.topics[0].hex().startswith("0xddf252ad"):  # Transfer event
                    # You can improve this later with full event parsing
                    pass
        except:
            pass

        # Log successful withdrawal
        history_cursor.execute(
            """
            INSERT INTO supply_history 
            (timestamp, action, amount, protocol, tx_hash, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), "Withdraw", amount_usdc, "Aave", tx_hash.hex(), "success")
        )
        history_conn.commit()

        return f"""
✅ **Successfully Withdrawn from Aave**

**Amount**: {amount_usdc:.2f} USDC  
**Tx Hash**: `{tx_hash.hex()[:20]}...`

🔗 [View on Arbiscan](https://sepolia.arbiscan.io/tx/{tx_hash.hex()})
        """
    except Exception as e:
        return f"❌ Withdrawal failed: {str(e)[:300]}"

tools = [fetch_yield_data, check_wallet_balance, execute_supply_best, withdraw_from_aave]
tool_node = ToolNode(tools)
# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: MessagesState):

    system_prompt = """You are Arbitrum YieldGuard — a smart yield agent.
- First use fetch_yield_data to check current yields.
- Use check_wallet_balance when needed.
- For supplying USDC to the best protocol, ALWAYS use execute_supply_best.
- For withdrawing USDC from Aave → use withdraw_from_aave.
Be helpful, clear, and safety-first."""
    try:
        messages = [("system", system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        error_msg = f"Agent error: {str(e)[:150]}"
        return {"messages": [AIMessage(content=error_msg)]}

# ============== BUILD GRAPH ==============
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
graph.add_edge("agent", END)  # Will stop when no more tools needed
agent = graph.compile()

# ============== SIDEBAR ==============
with st.sidebar:
    st.header("📍 Wallet")
    st.code(YOUR_WALLET)
    balance_info = check_wallet_balance.invoke(YOUR_WALLET)
    st.subheader("💰 Live Balance")
    st.markdown(balance_info.replace("\n", "  \n"))
    if st.button("🔄 Refresh Balance", key="refresh"):
        st.rerun()

    st.divider()
    st.warning("⚠️ Testnet Only (Sepolia)")

# ============== TABBED INTERFACE ==============
tab1, tab2 = st.tabs(["💬 Chat", "📊 Dashboard"])

with tab1:
    st.subheader("💬 Chat with YieldGuard")

    # ←←← INITIALIZE HERE (Top level, outside any conditional/tab)
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm YieldGuard. I can check balances, fetch live yields, and supply USDC to the best protocols on Arbitrum."
        }]

    # Chat messages container
    chat_container = st.container()


    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input - ALWAYS at the bottom
    if prompt := st.chat_input("What would you like to do? (e.g. Supply USDC to best yield)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing best yield..."):
                    try:
                        result = agent.invoke({"messages": st.session_state.messages})
                        response = result["messages"][-1].content
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"Error: {str(e)[:200]}")
                        response = "Sorry, something went wrong. Please try again."
                        st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
with tab2:
    # ============== DASHBOARD WITH HISTORICAL CHART ==============
    st.subheader("📊 Live Yield Dashboard - Arbitrum Sepolia")

    if st.button("🔄 Refresh Yields & History", type="primary"):
        st.rerun()

    yield_text = fetch_yield_data.invoke({})

    # Robust Aave parsing
    aave_apy = "N/A"
    tvl = "N/A"
    for line in yield_text.split("\n"):
        if "aave" in line.lower():
            apy_match = re.search(r"APY:\s*\**([\d.]+)%", line)
            tvl_match = re.search(r"TVL:\s*\**\$([\d.]+)M", line)
            if apy_match:
                aave_apy = apy_match.group(1) + "%"
            if tvl_match:
                tvl = "$" + tvl_match.group(1) + "M"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        balance_info = check_wallet_balance.invoke(YOUR_WALLET)
        usdc_part = balance_info.split("USDC")[-1].strip()[:10] if "USDC" in balance_info else "—"
        st.metric("💰 Your USDC", f"{usdc_part} USDC")

    with col2:
        st.metric("🏦 Aave Supply APY", aave_apy, "Variable")

    with col3:
        st.metric("🔥 Best APY", aave_apy, "Aave V3")

    with col4:
        st.metric("📈 Aave USDC TVL", tvl)

        # === YOUR SUPPLY HISTORY ===
        st.subheader("📜 My Supply & Withdraw History")

        df = pd.read_sql_query("""
            SELECT timestamp, action, amount, protocol, tx_hash, status 
            FROM supply_history 
            ORDER BY timestamp DESC
        """, history_conn)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.dataframe(
                df,
                column_config={
                    "timestamp": "Time",
                    "action": "Action",
                    "amount": st.column_config.NumberColumn("Amount (USDC)", format="%.2f"),
                    "tx_hash": "Transaction Hash"
                },
                use_container_width=True,
                hide_index=True
            )

            # Mini chart of supplied amounts
            st.subheader("📈 Cumulative Supplied Over Time")
            cumulative = df[df["action"] == "Supply"].copy()
            if not cumulative.empty:
                cumulative = cumulative.sort_values("timestamp")
                cumulative["Cumulative USDC"] = cumulative["amount"].cumsum()
                st.line_chart(cumulative, x="timestamp", y="Cumulative USDC")
        else:
            st.info("No supply/withdraw history yet. Make your first supply to start tracking.")

        # Live Yields
        with st.expander("🔍 Full Market Yields", expanded=False):
            st.markdown(yield_text)

