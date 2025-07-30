# VaultSeal

**VaultSeal** is a minimalist, encrypted secret manager built for the terminal. Store passwords, API tokens, or secure notes—all protected locally with AES encryption and a master password.

## Features

- AES-256 encryption via `cryptography`
- Local-only (no cloud or server!)
- Hidden master password prompt
- Copy secrets to clipboard (`--copy`)
- CLI: add, get, list, delete, change-password
- Fast, simple, scriptable

---

## Installation

```bash
pip install vaultseal
```
Or install from source:
```bash
git clone https://github.com/Nipfswd/vaultseal.git
cd vaultseal
pip install -e .
```

# Usage

```bash
vaultseal add github ghp_example_token
vaultseal get github --copy
vaultseal list
vaultseal delete github
vaultseal change-password
```

# Vault Location
Secrets are stored in an encrypted vault.json in the current working directory.

You can rename or move it freely if desired, or extend VaultSeal to support multiple vaults.

# License
MIT. See LICENSE for details.