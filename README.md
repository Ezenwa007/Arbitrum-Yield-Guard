# 🛡️ Arbitrum YieldGuard Agent

**Autonomous AI Yield Optimizer for Arbitrum**  

## 🎯 Overview

**Arbitrum YieldGuard** is an autonomous economic agent that intelligently manages USDC yield on Arbitrum.

It combines **real-time DeFi data**, **onchain execution**, and a **LangGraph-powered AI agent** so users can simply chat with it, e.g., “Supply 500 USDC to the best yield”, and the agent handles research, decision-making, approvals, and transactions securely.

## ✨ Key Features

- **Autonomous AI Agent**: Powered by LangGraph + OpenRouter
- **Real-time Yield Intelligence**: Fetches live APYs from DefiLlama across Arbitrum protocols
- **One-Click Smart Supply**: Automatically supplies to the best protocol
- **Safe Withdrawals**: Full withdraw support from Aave
- **Live Dashboard**: Balances, APY metrics, TVL and cumulative supply history
- **Persistent History**: SQLite-backed supply/withdraw log with interactive charts
- **Natural Language Chat**: Talk to your agent like a human
- **Testnet Safety**: Built exclusively for Arbitrum (Sepolia for now) 
- Chat Interface
- Live Dashboard with metrics and history chart

## 🛠️ Tech Stack

- **Agent Framework** - LangGraph + LangChain
- **LLM** - OpenRouter
- **Blockchain** - Web3.py + Arbitrum Sepolia
- **Yield Data** - DefiLlama API
- **Database** - SQLite3
- **Smart Contracts** - Aave V3 (via direct calls)

##  How It Works
1. User chats with the agent (e.g., "Supply 1000 USDC")
2. Agent uses tools:
   - fetch_yield_data() → checks current best yields
   - check_wallet_balance() → verifies funds
   - execute_supply_best() → approves + supplies to Aave
3. Onchain execution via Web3.py with proper EIP-1559 gas
4. History & metrics automatically logged and visualized

## Future Roadmap
- Multi-protocol auto-selection (Aave + Spark + others)
- Agent-to-agent negotiation
- Onchain reputation & performance tracking
- Account Abstraction (ERC-4337) integration for gas sponsorship
- Cross-chain yield opportunities
- Risk-aware rebalancing logic
- Deployment as a persistent onchain agent




