# 🛡️ Arbitrum YieldGuard Agent

**Smart Autonomous Yield Optimizer on Arbitrum Sepolia**

An intelligent AI agent that helps you manage USDC yields on Arbitrum by automatically fetching live APYs, supplying to the best protocol (Aave V3), and tracking your deposit/withdrawal history.

---

## ✨ Features

- **Natural Language Chat Interface** - Talk to the agent like "Supply 50 USDC to best yield"
- **Live Yield Dashboard** - Real-time Aave APY and TVL from DefiLlama
- **Smart Auto-Supply** - One-click supply to Aave with proper approvals + EIP-1559 gas
- **Withdraw Support** - Withdraw USDC from Aave directly from chat or dashboard
- **Persistent Transaction History** - All your supplies and withdrawals are logged
- **Historical APY Chart** - Tracks Aave USDC APY over time
- **Live Wallet Balance** - Shows ETH + USDC balance in sidebar

---

## 🛠 Tech Stack

- **Frontend**: Streamlit
- **AI Agent**: LangGraph + LangChain + OpenRouter
- **Blockchain**: Web3.py (Arbitrum Sepolia)
- **Data**: DefiLlama API + SQLite
- **Persistence**: `supply_history.db` + `yields.db`

---

## How to UseChat Tab
- Check my balance
- What is the current Aave APY?
- Supply 25 USDC to best yield
- Withdraw 10 USDC from Aave

---

## Dashboard Tab
- Live metrics (APY, TVL, Balance)
- Historical APY chart
- Full supply/withdraw transaction history
- Quick action buttons

---

## Future Enhancements 
- Auto-compounding
- Email notifications
- Portfolio analytics

---
