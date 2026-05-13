# SovereignVault

SovereignVault is a decentralized encrypted memory infrastructure for autonomous AI agents, built on the [0G ecosystem](https://0g.ai?utm_source=chatgpt.com).

It enables AI agents to securely store, synchronize, and recover private memory across devices while maintaining user ownership and sovereignty.

## Overview

Modern AI agents often lose context when applications restart or local storage is wiped. SovereignVault solves this by giving each agent:

- Private encrypted memory
- Local persistence
- Decentralized backup on 0G Storage
- Automatic recovery from 0G
- Sync monitoring dashboard

This creates a sovereign memory layer for AI agents that is portable, tamper-resistant, and user-controlled.

---

## Core Features

### Encrypted Agent Memory
Each agent stores memories in an encrypted vault using Fernet symmetric encryption.

### Local Fast Storage
Encrypted vaults are cached locally for fast access.

### 0G Decentralized Sync
Encrypted vault files are automatically uploaded to 0G storage.

### Automatic Recovery
If a local vault is missing, users can restore it from 0G by selecting the agent and clicking recover.

### Sync Status Dashboard
A built-in dashboard displays:

- Agent sync status
- Last sync time
- 0G root hash references

---

## Architecture

```text
User Input
    ↓
AI Agent
    ↓
Encrypt Memory (Fernet)
    ↓
Local Vault File
    ↓
Sync to 0G Storage
    ↓
Store Root Hash in SQLite
    ↓
Recovery via Agent Selection
```

---

## Tech Stack

- Python
- Streamlit
- SQLite
- cryptography
- requests
- Web3.py
- 0G Storage API

---

## Project Structure

```text
sovereign-vault/
├── app.py
├── vault_utils.py
├── vault_index_db.py
├── og_sync.py
├── contract_utils.py
├── crypto_utils.py
├── data/
│   └── vaults/
├── vault_index.db
├── requirements.txt
└── README.md
```

---

## How It Works

### Save Memory

When an agent stores memory:

1. Memory is encrypted locally
2. Saved to local vault file
3. Uploaded to 0G storage
4. Root hash saved in SQLite index

### Restore Memory

When local storage is missing:

1. User selects agent
2. Clicks **Restore Vault**
3. Root hash fetched from SQLite
4. Encrypted vault pulled from 0G
5. Local vault recreated
6. Agent resumes with full memory

---

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd sovereign-vault
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

---

## Environment Variables

Create a `.env` file:

```env
MEMORY_ENCRYPTION_KEY=your_generated_key
RPC_URL=your_0g_rpc_url
PRIVATE_KEY=your_wallet_private_key
```

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Use Cases

SovereignVault can power:

- AI personal assistants
- autonomous trading agents
- decentralized copilots
- private agent marketplaces
- persistent AI identities
- multi-agent collaboration systems

---

## Why 0G

SovereignVault uses 0G because it offers infrastructure designed for decentralized AI applications.

This makes it possible to combine:

- verifiable storage
- decentralized persistence
- AI-native architecture
- user-owned memory

---

## Future Roadmap

- Versioned memory snapshots
- Semantic memory search
- Agent-to-agent memory sharing
- Wallet-derived encryption keys
- Cross-device sovereign recovery
- On-chain memory proofs

---

## Hackathon Vision

SovereignVault demonstrates how AI agents can own persistent, encrypted, portable memory using decentralized infrastructure.

This creates a future where autonomous agents are:

- sovereign
- recoverable
- user-controlled
- trust-minimized

---

## License

MIT License
