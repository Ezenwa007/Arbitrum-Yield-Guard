# 🛡️ Arbitrum YieldGuard Agent

**Autonomous AI Yield Optimizer for Arbitrum**  

## 🎯 Overview

**Arbitrum YieldGuard** is an autonomous economic agent that intelligently manages USDC yield on Arbitrum.

It combines **real-time DeFi data**, **onchain execution**, and a **LangGraph-powered AI agent** so users can simply chat with it, e.g., “Supply 500 USDC to the best yield”, and the agent handles research, decision-making, approvals, and transactions securely.

## ✨ Key Features

- **🧠 Autonomous AI Agent**: Powered by LangGraph + OpenRouter
- **📡 Real-time Yield Intelligence**: Fetches live APYs from DefiLlama across Arbitrum protocols
- **⚡ One-Click Smart Supply**: Automatically supplies to the best protocol
- **🔄 Safe Withdrawals** — Full withdraw support from Aave
- **📊 Live Dashboard** — Balances, APY metrics, TVL, and cumulative supply history
- **📜 Persistent History** — SQLite-backed supply/withdraw log with interactive charts
- **💬 Natural Language Chat** — Talk to your agent like a human
- **🛡️ Testnet Safety** — Built exclusively for Arbitrum Sepolia

## 🖥️ Screenshots

*(Add screenshots here after running the app)*

- Chat Interface
- Live Dashboard with metrics and history chart

## 🛠️ Tech Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Frontend           | Streamlit                           |
| Agent Framework    | LangGraph + LangChain               |
| LLM                | OpenRouter (free tier models)       |
| Blockchain         | Web3.py + Arbitrum Sepolia          |
| Yield Data         | DefiLlama API                       |
| Database           | SQLite3                             |
| Smart Contracts    | Aave V3 (via direct calls)          |

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd arbitrum-yieldguard
